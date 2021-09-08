# THE-CROSS - Smart Traffic Control Application

- 본 프로젝트는 OSS 개발자 대회 제출용 프로젝트 입니다.

THE-CROSS - 사용법 안내
-----------------------
1. Custom Model 설치
   - 해당 Github의 customDetector 폴더를 참조하세요.
2. 카메라 설정법
   1. 프로그램 화면 우측하단에서, 원하시는 영역을 찾아 영역설정 버튼을 클릭합니다.
   2. 버튼 클릭 시, 팝업되는 Window 창에 실시간 카메라 영상이 출력될 때까지 기다립니다.
   3. 팝업된 Window 창에 실시칸 카메라 영상이 출력되면, 화면에 4개의 꼭짓점을 클릭하여 사각형 형태의 영역을 설정합니다.
   4. 꼭짓점을 4개 초과 클릭 시, 이전에 클릭한 4개의 꼭짓점은 초기화 되며, 다시 꼭짓점들을 클릭하여 사각형 형태의 영역을 재설정하면 됩니다.
   5. 저장하려면 키보드 "Q" Key를 눌러 저장하면 됩니다.

3. 시간 증감값 설정법
   1. 좌측 하단에 존재하는 여러개의 값들을 원하시는 값으로 변경합니다. 
   2. "설정 변경" 버튼을 누릅니다.

THE-CROSS - 내부 구조
--------------------------------------
1. Images (Folder)
    - GUI에 사용되는 이미지가 저장되어 있음
2. customDetector (Folder)
    - 구급차, 휠체어, 지팡이, 유모차를 인식하는 모델이 저장되어 있음
    - efficientdet_d0_coco17_tpu-32 모델을 Tensorflow Object Detection API를 통해 전이학습 하였음
3. Camera.py
    - VideoThread : 카메라를 실질적으로 입력 받고 처리하는 클래스
    - CameraSetup : 카메라를 설정하는 클래스
4. FileManager.py
    - 파일 저장 주소와 초기값이 저장되어있음
    - configManager : 파일 입출력 및 저장
5. ImageDetector.py
    - Detector : Image 배열을 입력받아 보행자가 있다고 예측된 값을 반환하는 메소드
    - CustomDetector : Image 배열을 입력받아 [휠체어, 유모차, 지팡이, 구급차] 가 있다고 예측된 값을 반환하는 메소드
6. ImageUtils.py
    - cvImgToQtImg : OpenCV로 불러온 Image 배열을 QtImg 객체로 반환하는 메소드
    - resizeCVIMG : OpenCV로 불러온 Image 배열의 크기를 변경하는 메소드
    - cvImgToPixmap : OpenCV로 불러온 Image 배열을 PyQT의 Pixmap 객체로 반환하는 메소드
    - draw_area : OpenCV로 불러온 Image 배열과 4개의 꼭짓점을 인수로 받아 Image위에 사각형 영역을 그려서 반환하는 메소드
    - isSpotInRect : 4개의 꼭짓점과 특정 점을 인수로 받아 특정 점이 4개의 꼭짓점으로 이루어진 사각형 영역 내에 있는지 반환하는 메소드
7. SirenDetector.py
    - SirenDetector : 2초 단위로 소리를 입력받아, 해당 소리가 사이렌 소리인지 반환하는 메소드
8. main.py
    - Main : 프로그램의 중요한 처리를 담당하는 클래스
    - init , initUI : 프로그램 시작 시, GUI 생성
    - processing : Camera.py로 부터 전달 받은 이미지를 처리하여, 신호등을 제어함
    - TimerMethod : 신호등 시간을 실질적으로 제어함
