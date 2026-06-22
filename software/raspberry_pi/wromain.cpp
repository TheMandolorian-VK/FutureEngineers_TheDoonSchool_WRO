#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>

int main() {
    // Open webcam (forces DirectShow backend on Windows)
    cv::VideoCapture cap(0, cv::CAP_DSHOW);

    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open camera feed." << std::endl;
        return -1;
    }

    cv::Mat frame, hsv;
    cv::Mat mask_green, mask_red1, mask_red2, mask_red, mask_combined;
    
    std::cout << "Press 'q' inside the video window to exit." << std::endl;

    while (true) {
        cap >> frame;
        if (frame.empty()) break;
        cv::cvtColor(frame, hsv, cv::COLOR_BGR2HSV);

        cv::Scalar lower_green(35, 50, 50);
        cv::Scalar upper_green(85, 255, 255);
        cv::inRange(hsv, lower_green, upper_green, mask_green);

        cv::inRange(hsv, cv::Scalar(0, 70, 50), cv::Scalar(10, 255, 255), mask_red1);
        cv::inRange(hsv, cv::Scalar(170, 70, 50), cv::Scalar(180, 255, 255), mask_red2);
        cv::bitwise_or(mask_red1, mask_red2, mask_red);
        cv::bitwise_or(mask_green, mask_red, mask_combined);

        cv::GaussianBlur(mask_combined, mask_combined, cv::Size(5, 5), 0);

        std::vector<std::vector<cv::Point>> contours;
        std::vector<cv::Vec4i> hierarchy;
        cv::findContours(mask_combined, contours, hierarchy, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

        for (size_t i = 0; i < contours.size(); i++) {
            if (cv::contourArea(contours[i]) > 700) { // Filter noise
                cv::Rect bounding_box = cv::boundingRect(contours[i]);

                int cx = bounding_box.x + bounding_box.width / 2;
                int cy = bounding_box.y + bounding_box.height / 2;
            
                if(cx >= 0 && cx < hsv.cols && cy >= 0 && cy < hsv.rows) {
                    cv::Vec3b hsv_pixel = hsv.at<cv::Vec3b>(cy, cx);
                    int hue = hsv_pixel[0];

                    cv::Scalar box_color;
                    std::string label;

                    // Evaluate hue ranges to match labels dynamically
                    if (hue >= 35 && hue <= 85) {
                        box_color = cv::Scalar(0, 255, 0); // Green bounding box (BGR)
                        label = "Green Object";
                    } else {
                        box_color = cv::Scalar(0, 0, 255); // Red bounding box (BGR)
                        label = "Red Object";
                    }

                    // Draw the rectangle and label matching the tracked colors
                    cv::rectangle(frame, bounding_box, box_color, 2);
                    cv::putText(frame, label, cv::Point(bounding_box.x, bounding_box.y - 5),
                                cv::FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1);
                }
            }
        }
        cv::imshow("WRO Dual Color Tracking", frame);

        if (cv::waitKey(30) == 'q') {
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}
