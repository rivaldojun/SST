import cv2
import mediapipe as mp

# Initialiser MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Charger une vidéo ou utiliser la webcam
cap = cv2.VideoCapture(0)  # Utiliser 0 pour la webcam intégrée, ou spécifier le chemin de la vidéo

while cap.isOpened():
    # Lire la frame de la vidéo
    ret, frame = cap.read()
    if not ret:
        break
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Obtenir les landmarks de la pose
    results = pose.process(gray)
    # Dessiner les landmarks sur l'image
    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    # Afficher l'image avec les landmarks
    cv2.imshow('Pose Landmarks Detection', frame)
    # Sortir de la boucle si la touche 'q' est pressée
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# Libérer les ressources
cap.release()
cv2.destroyAllWindows()
