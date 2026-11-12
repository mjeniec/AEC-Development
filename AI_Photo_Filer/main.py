from pathlib import Path
from PIL import Image
import cv2
import sqlite3

TEST_FOLDER = Path(__file__).resolve().parent / "test_photos"
MODELS_FOLDER = Path(__file__).resolve().parent / "models"
DATABASE_PATH = Path(__file__).resolve().parent / "known_people"


YUNET_MODEL_PATH = MODELS_FOLDER / "face_detection_yunet_2023mar.onnx"
SFACE_MODEL_PATH = MODELS_FOLDER / "face_recognition_sface_2021dec.onnx"

OUTPUT_FOLDER = Path(__file__).resolve().parent / "output_folder"
OUTPUT_FOLDER.mkdir(exist_ok=True)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("""
    CREATE TABLE IF NOT EXISTS people (
        person_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
""")

connection.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        embedding_id INTEGER PRIMARY KEY,
        person_id INTEGER NOT NULL,
        embedding BLOB NOT NULL,
        FOREIGN KEY (person_id) REFERENCES people(person_id)
    )
""")

# connection.execute("""
#     INSERT INTO people (name)
#     VALUES (?)
# """, ("Matt",))

connection.commit()

results = connection.execute("SELECT * FROM people").fetchall()
print(results)

connection.close()



# CREATE FACE DETECTOR # 

face_detector = cv2.FaceDetectorYN.create(
    model=str(YUNET_MODEL_PATH),
    config="",
    input_size=(320, 320),
    score_threshold=0.6
)

# CREATE FACE RECOGNISER # 


face_recogniser = cv2.FaceRecognizerSF.create(
    model=str(SFACE_MODEL_PATH),
    config=""
)



# HELPER FUNCTIONS #

def find_images(folder):

    images = []

    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(path)

    return images


# def count_extensions(images):

#     counts = {}

#     for image in images:
        
#         extension = image.suffix.lower()

#         counts.setdefault(extension, 0)
#         counts[extension] += 1

#     return counts


# def get_image_dimensions(image_path): 

#     with Image.open(image_path) as img:
#         image_dims = img.size

#     return image_dims 


# def get_pixel_colour(image_path, x, y):

#     with Image.open(image_path) as img:
#         pixel_colour = img.getpixel((x, y))

#     return pixel_colour


def detect_faces(image, detector):

    
    h, w = image.shape[0:2]

    detector.setInputSize((w, h))

    _, faces = detector.detect(image)
    
    return faces 



def generate_embedding(image, face, recogniser):

    aligned_face = recogniser.alignCrop(image, face)
    embedding = recogniser.feature(aligned_face) 

    return embedding


# FIND PHOTOS #

photos = find_images(TEST_FOLDER)


# GENERATE EMBEDDINGS FOR FACES #

photo_data = {}

for photo in photos:

    embeddings = []

    image = cv2.imread(str(photo))
    faces = detect_faces(image, face_detector)

    if faces is None:
        faces = []

    for face in faces:
        embedding = generate_embedding(image, face, face_recogniser)

        embeddings.append(embedding)

    photo_data[photo.name] = embeddings

for photo, embeddings in photo_data.items():

    if len(embeddings) > 0:

        embedding = embeddings[0]

        print("Shape:", embedding.shape)
        print("Data type:", embedding.dtype)
        print("Number of bytes:", len(embedding.tobytes()))

        break





    
    
# for photo, embeddings in photo_data.items():
#     print(photo, len(embeddings))








# DRAW RECTANGLES AROUND FACES  #

# for counter, photo in enumerate(photos, start=1):

#     image = cv2.imread(str(photo))
#     faces = detect_faces(image, face_detector)

#     if faces is None:
#         faces = []

#     for face in faces:

#         point_1 = (int(face[0]), int(face[1]))
#         point_2 = (int(face[0] + face[2]), int(face[1] + face[3]))
       
#         cv2.rectangle(image, point_1, point_2, (0, 255, 0), 2)
#         print(f'Confidence: {face[14]}')
        
#     output_path = OUTPUT_FOLDER / f"faces_debug{counter:03d}.jpg"
#     success = cv2.imwrite(str(output_path), image)
#     print(f"Photo {counter} : {len(faces)} faces detected, saved: {success}")








# PRINT DIAGNOSTICS # 

# photo = photos[1]
# image = cv2.imread(str(photo))
# faces = detect_faces(image, face_detector)


# aligned_face = face_recogniser.alignCrop(image, faces[0])
# embedding = face_recogniser.feature(aligned_face)

# cv2.imwrite(str(OUTPUT_FOLDER / "aligned_face.jpg"), aligned_face)

#print(get_pixel_coelour(photo, 100, 100))



# def main():

#     images = find_images(TEST_FOLDER)

#     print("Number of images found:", len(images))

#     for image in images:
#         print(image)


# if __name__ == "__main__":
#     main()