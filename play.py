from ultralytics import YOLO
import cv2
from enum import Enum


class PlayMode(Enum):
    Shoot = 1
    Defend = 2
    Ammo = 3
    Standby = 4
    Unrecognized = 5

    def __str__(self):
        return self.name
    
    def copy(self):
        return self.__class__(self.value)   
def play_live_camera():
    # Load a model
    model = YOLO('yolov8n-pose.pt')  # load an official model

    # Predict with the model

    cap = cv2.VideoCapture(0)

    font = cv2.FONT_HERSHEY_SIMPLEX
    prev_mode = PlayMode.Unrecognized
    actual_mode = PlayMode.Unrecognized
    status_frame_count = 0
    ammo = 0

    while True:
        ret, frame = cap.read()
        results = model(frame)
        keypoints = results[0].keypoints
        x_right_hand, y_right_hand = int(keypoints.xy[0,10,0]), -int(keypoints.xy[0,10,1])
        x_left_hand, y_left_hand = int(keypoints.xy[0,9,0]), -int(keypoints.xy[0,9,1])

        x_right_waist, y_right_waist = int(keypoints.xy[0,12,0]), -int(keypoints.xy[0,12,1])
        x_left_waist, y_left_waist = int(keypoints.xy[0,11,0]), -int(keypoints.xy[0,11,1])

        x_right_elbow, y_right_elbow = int(keypoints.xy[0,8,0]), -int(keypoints.xy[0,8,1])
        x_left_elbow, y_left_elbow = int(keypoints.xy[0,7,0]), -int(keypoints.xy[0,7,1])
        
        x_right_shoulder, y_right_shoulder = int(keypoints.xy[0,6,0]), -int(keypoints.xy[0,6,1])
        x_left_shoulder, y_left_shoulder = int(keypoints.xy[0,5,0]), -int(keypoints.xy[0,5,1])

        if (x_right_hand > x_left_hand) & (y_right_hand > y_left_elbow) & (y_left_hand > y_right_elbow):
            cv2.putText(frame, 'Defense mode', (200,200), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
            temp_mode = PlayMode.Defend
            
        elif (x_right_hand < x_left_hand) & (y_right_hand > y_right_shoulder) & (y_left_hand > y_left_shoulder):
            cv2.putText(frame, 'Ammo mode', (200,200), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
            temp_mode = PlayMode.Ammo

        elif (x_right_hand < x_left_hand) & (y_right_hand > y_right_elbow) & (y_left_hand > y_left_elbow):
            cv2.putText(frame, 'Shoot mode', (200,200), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
            temp_mode = PlayMode.Shoot

        elif (x_right_hand < x_left_hand) & (y_right_hand < y_right_waist) & (y_left_hand < y_left_waist):
            cv2.putText(frame, 'Standby mode', (200,200), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
            temp_mode = PlayMode.Standby

        else:
            cv2.putText(frame, 'Unrecognized mode', (200,200), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
            temp_mode = PlayMode.Unrecognized

        if prev_mode == PlayMode.Standby:
            status_frame_count +=1
            if status_frame_count > 5:
                if temp_mode is not PlayMode.Unrecognized:
                    actual_mode = temp_mode.copy()
                    prev_mode = temp_mode.copy()

                    if actual_mode == PlayMode.Shoot:
                        ammo -=1
                    elif actual_mode == PlayMode.Ammo:
                        ammo +=1
                status_frame_count = 0

        if temp_mode == PlayMode.Standby:
            prev_mode = PlayMode.Standby
            status_frame_count = 0


        cv2.putText(frame, f'Last Play Mode: {actual_mode.name}', (0,50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f'Ammo status: {str(ammo)}', (0,400), font, 0.5, (0, 0, 255), 2, cv2.LINE_AA)

        # for i, kpt in enumerate(keypoints.xy[0,...]):
        #     x, y = int(kpt[0]), int(kpt[1])
        #     cv2.putText(frame, str(i), (x,y), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

            # cv2.circle(frame, (x, y), radius=3, color=(0, 255, 0), thickness=-1)
        cv2.imshow('Live Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    play_live_camera()