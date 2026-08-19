import sys, time,cv2,numpy as np
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial=None

CAMERA_INDEX=0
CAMERA_WIDTH,CAMERA_HEIGHT=1280,720
CAMERA_FPS=60
SERIAL_BAUD=115200
SERIAL_PORT=None
COMMAND_PERIOD=1/25

KP, KD=32.0,10.0
STEERING_MIN,STEERING_MAX=-45.0,45.0
MAX_DERIVATIVE=3.0
CENTER_DEADZONE=0.05
BASE_SPEED,MIN_SPEED,MAX_SPEED=165,75,210
PILLAR_BIAS=12.0
KNOWN_HEIGHT_CM=20.0
FOCAL_LENGTH_PX=700.0

# Top-middle pillar ROI
ROI_X1,ROI_X2=0.30,0.70
ROI_Y1,ROI_Y2=0.00,0.42
LINE_ROI_TOP=0.55

MIN_AREA=100
PILLAR_MIN_AREA=250
LINE_MIN_AREA=80
MORPH=np.ones((5,5),np.uint8)

# OpenCV CIELAB: L,a,b are stored as 0..255.
# Tune these values with the camera on the real field.
LAB_RANGES={
    "red":((45,150,125),(210,215,190)),
    "green":((35,70,105),(210,135,175)),
    "orange":((80,135,145),(245,195,220)),
    "blue":((25,115,55),(190,165,130)),
    "purple":((30,140,75),(190,205,145))
}

previous_error=0.0
previous_error_time=None

class NavigationMode:
    SEARCH="SEARCH"
    TRACK="TRACK"
    RED_PILLAR="RED_PILLAR"
    GREEN_PILLAR="GREEN_PILLAR"

class ESP32Controller:
    def __init__(self,port=None,baudrate=SERIAL_BAUD):
        self.port_override=port
        self.baudrate=baudrate
        self.serial=None
        self.connected=False
        self.last_send=0.0

    def find_port(self):
        if self.port_override:return self.port_override
        if serial is None:return None
        candidates=[]
        for p in serial.tools.list_ports.comports():
            text=f"{p.device} {p.description} {p.manufacturer}".lower()
            score=0
            for word,value in (("esp32",8),("cp210",5),("ch340",5),("usb",2)):
                if word in text:score+=value
            candidates.append((score,p.device))
        return max(candidates)[1] if candidates else None

    def connect(self):
        if serial is None:return False
        for _ in range(5):
            port=self.find_port()
            if port:
                try:
                    self.serial=serial.Serial(port,self.baudrate,timeout=.02,write_timeout=.05)
                    time.sleep(2)
                    self.serial.reset_input_buffer()
                    self.connected=True
                    print("ESP32 connected:",port)
                    return True
                except (serial.SerialException,OSError):
                    pass
            time.sleep(1)
        return False

    def send(self,steering,pwm,mode,force=False):
        if not self.connected:return
        now=time.perf_counter()
        if not force and now-self.last_send<COMMAND_PERIOD:return
        steering=np.clip(steering,STEERING_MIN,STEERING_MAX)
        pwm=int(np.clip(pwm,-255,255))
        try:
            self.serial.write(f"CMD,{steering:.2f},{pwm},{mode}\n".encode())
            self.last_send=now
        except (serial.SerialException,OSError):
            self.connected=False

    def stop(self):
        if self.connected:
            try:self.serial.write(b"STOP\n")
            except Exception:pass

    def close(self):
        if self.serial:
            try:self.serial.close()
            except Exception:pass
        self.connected=False

class IMUInterface:
    def __init__(self):
        self.available=False
        self.gyro_z_dps=0.0
    def update(self):return False

class ToFInterface:
    def __init__(self):
        self.available=False
        self.distance_cm=None
    def update(self):return False
    def get_distance(self):return self.distance_cm

def open_camera():
    backend=cv2.CAP_V4L2 if sys.platform.startswith("linux") else cv2.CAP_ANY
    cap=cv2.VideoCapture(CAMERA_INDEX,backend)
    if not cap.isOpened():
        cap=cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS,CAMERA_FPS)
    return cap

def clean_mask(mask):
    mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,MORPH)
    return cv2.morphologyEx(mask,cv2.MORPH_CLOSE,MORPH)

def color_mask(lab,color,tolerance=20):
    lo=np.array(LAB_RANGES[color][0],dtype=np.int16)
    hi=np.array(LAB_RANGES[color][1],dtype=np.int16)
    expansion=int(tolerance*.35)
    lo=np.clip(lo-expansion,0,255).astype(np.uint8)
    hi=np.clip(hi+expansion,0,255).astype(np.uint8)
    return clean_mask(cv2.inRange(lab,lo,hi))

def black_mask(lab,tolerance=20):
    limit=int(np.clip(45+tolerance,35,100))
    return clean_mask(cv2.inRange(lab,np.array((0,0,0)),np.array((limit,255,255))))

def detect_objects(mask,color,xoff=0,yoff=0,min_area=MIN_AREA):
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    out=[]
    for contour in contours:
        area=cv2.contourArea(contour)
        if area<min_area:continue
        x,y,w,h=cv2.boundingRect(contour)
        m=cv2.moments(contour)
        cx=m["m10"]/m["m00"] if m["m00"] else x+w/2
        cy=m["m01"]/m["m00"] if m["m00"] else y+h/2
        out.append({"color":color,"area":area,"x":x+xoff,"y":y+yoff,
                    "w":w,"h":h,"cx":cx+xoff,"cy":cy+yoff,"contour":contour})
    return out

def detect_pillars(lab,w,h,tolerance):
    x1,x2=int(w*ROI_X1),int(w*ROI_X2)
    y1,y2=int(h*ROI_Y1),int(h*ROI_Y2)
    roi=lab[y1:y2,x1:x2]
    detections=[]
    mask=np.zeros((y2-y1,x2-x1),np.uint8)
    for color in ("red","green"):
        m=color_mask(roi,color,tolerance)
        mask=cv2.bitwise_or(mask,m)
        detections+=detect_objects(m,color,x1,y1,PILLAR_MIN_AREA)
    if not detections:return None,mask,(x1,y1,x2,y2)
    target=max(detections,key=lambda d:d["area"]*(1+d["h"]/(y2-y1)))
    return target,mask,(x1,y1,x2,y2)

def detect_lines(lab,w,h,tolerance):
    y0=int(h*LINE_ROI_TOP)
    roi=lab[y0:h,:]
    lines=[]
    mask=np.zeros((h-y0,w),np.uint8)
    for color in ("orange","blue"):
        m=color_mask(roi,color,tolerance)
        mask=cv2.bitwise_or(mask,m)
        lines+=detect_objects(m,color,0,y0,LINE_MIN_AREA)
    lines=[d for d in lines if d["w"]>=5 and d["h"]>=5]
    left=[d for d in lines if d["cx"]<w/2]
    right=[d for d in lines if d["cx"]>=w/2]
    l=max(left,key=lambda d:d["area"]) if left else None
    r=max(right,key=lambda d:d["area"]) if right else None
    return l,r,mask

def line_error(left,right,w):
    if left and right:center=(left["cx"]+right["cx"])/2
    elif left:center=left["cx"]+w*.4
    elif right:center=right["cx"]-w*.4
    else:return None
    return float(np.clip((center-w/2)/(w/2),-1,1))

def centering_error(cx,w):
    e=(cx-w/2)/(w/2)
    return 0.0 if abs(e)<=CENTER_DEADZONE else float(np.clip(e,-1,1))

def reset_pd():
    global previous_error,previous_error_time
    previous_error=0.0
    previous_error_time=None

def pd(error):
    global previous_error,previous_error_time
    now=time.perf_counter()
    if previous_error_time is None:d=0.0
    else:
        dt=max(now-previous_error_time,.001)
        d=np.clip((error-previous_error)/dt,-MAX_DERIVATIVE,MAX_DERIVATIVE)
    output=np.clip(KP*error+KD*d,STEERING_MIN,STEERING_MAX)
    previous_error,previous_error_time=error,now
    return float(output)

def pillar_bias(steering,target,w):
    if target["color"]=="red":
        bias=PILLAR_BIAS if target["cx"]<w/2 else PILLAR_BIAS*.35
        side="RIGHT"
    else:
        bias=-PILLAR_BIAS if target["cx"]>w/2 else -PILLAR_BIAS*.35
        side="LEFT"
    return float(np.clip(steering+bias,STEERING_MIN,STEERING_MAX)),side

def speed_for(steering,pillar=False,distance=None):
    speed=BASE_SPEED-80*abs(steering)/STEERING_MAX
    if pillar:speed-=15
    if distance is not None and distance<30:speed-=25
    return int(np.clip(speed,MIN_SPEED,MAX_SPEED))

def distance_from_height(h):
    return KNOWN_HEIGHT_CM*FOCAL_LENGTH_PX/h if h>0 else None

def draw_target(frame,d):
    x,y,w,h=map(int,(d["x"],d["y"],d["w"],d["h"]))
    cx,cy=int(d["cx"]),int(d["cy"])
    color=(0,0,255) if d["color"]=="red" else (0,255,0)
    cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
    cv2.circle(frame,(cx,cy),5,color,-1)
    cv2.putText(frame,d["color"].upper(),(x,max(20,y-8)),
                cv2.FONT_HERSHEY_SIMPLEX,.6,color,2)

def main():
    cap=open_camera()
    if cap is None:
        print("Camera unavailable")
        return

    esp=ESP32Controller(SERIAL_PORT)
    esp.connect()
    imu,tof=IMUInterface(),ToFInterface()
    cv2.namedWindow("WRO Vision",cv2.WINDOW_NORMAL)
    cv2.createTrackbar("Tolerance","WRO Vision",20,60,lambda _:None)
    last=time.perf_counter()

    try:
        while True:
            ok,frame=cap.read()
            if not ok:break
            h,w=frame.shape[:2]
            tolerance=cv2.getTrackbarPos("Tolerance","WRO Vision")
            imu.update()
            tof.update()

            blurred=cv2.GaussianBlur(frame,(5,5),0)
            lab=cv2.cvtColor(blurred,cv2.COLOR_BGR2LAB)

            pillar,pillar_mask,roi=detect_pillars(lab,w,h,tolerance)
            left,right,line_mask=detect_lines(lab,w,h,tolerance)
            error=line_error(left,right,w)
            distance=tof.get_distance()
            side="NONE"

            if pillar:
                error=centering_error(pillar["cx"],w)
                mode=NavigationMode.RED_PILLAR if pillar["color"]=="red" else NavigationMode.GREEN_PILLAR
                steering=pd(error)
                steering,side=pillar_bias(steering,pillar,w)
                if distance is None:distance=distance_from_height(pillar["h"])
            elif error is not None:
                mode=NavigationMode.TRACK
                steering=pd(error)
            else:
                mode=NavigationMode.SEARCH
                steering=0.0
                reset_pd()

            motor=speed_for(steering,pillar is not None,distance)
            esp.send(steering,motor,"DRIVE")

            x1,y1,x2,y2=roi
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,255),2)
            cv2.putText(frame,"PILLAR ROI",(x1+8,y1+25),
                        cv2.FONT_HERSHEY_SIMPLEX,.6,(0,255,255),2)

            if pillar:draw_target(frame,pillar)
            for line in (left, right):
                if line:
                    cv2.circle(frame,(int(line["cx"]),int(line["cy"])),9,(255,255,0),2)

            cv2.line(frame,(w//2,0),(w//2,h),(180,180,180),1)
            now=time.perf_counter()
            fps=1/max(now-last,.001)
            last=now
            status=f"{mode} | steer {steering:+.1f} | motor {motor} | {side} | {fps:.0f} FPS"
            cv2.rectangle(frame,(8,h-42),(min(w-8,760),h-8),(0,0,0),-1)
            cv2.putText(frame,status,(18,h-18),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),2)

            cv2.imshow("WRO Vision",frame)
            key=cv2.waitKey(1)&0xff
            if key==27:break
            if key==ord(" "):
                esp.send(0,0,"STOP",True)
                reset_pd()
    finally:
        esp.stop()
        esp.close()
        cap.release()
        cv2.destroyAllWindows()

if __name__=="__main__":
    main()



For reliable competition performance, calibrate `LAB_RANGES` using actual frames from the Pi Camera 3 at the venue rather than relying on the example values.
