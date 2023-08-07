import cv2
import mediapipe as mp

def main():
    # Mediapipe Pose 모듈 초기화
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    # 웹캠 또는 카메라에서 비디오를 가져오기 위해 VideoCapture 객체 생성
    cap = cv2.VideoCapture(0)

    while True:
        ret, image = cap.read()

        if not ret:
            break

        # 이미지를 BGR에서 RGB로 변환
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 포즈 추정 수행
        results = pose.process(image_rgb)

        # 포즈 점 그리기
        if results.pose_landmarks:
            mp_pose.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                   mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                   mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                                   )

        # 화면에 이미지 표시
        cv2.imshow('Pose Estimation', image)

        # 'q'를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 사용이 끝나면 비디오 캡처 해제 및 창 닫기
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
