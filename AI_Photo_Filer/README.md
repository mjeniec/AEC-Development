# AI Photo Filer

### Local AI-Powered Family Photo and Video Organiser

**Project:** AEC Development — AI Photo Filer  
**Language:** Python  
**Status:** Work in Progress — Initial Prototype

---

## 1. Project Overview

AI Photo Filer is a Python application being developed to automatically organise personal photographs and videos using facial recognition.

The application uses pretrained AI models to detect faces, generate numerical representations of facial features and identify individuals across a collection of photographs.

The long-term objective is to organise a family photo and video library automatically, grouping files according to the people appearing in them.

**All image processing and facial recognition are intended to run locally**, without uploading personal photographs to external AI services.

The project also serves as a practical introduction to Python programming, computer vision, AI models and database management.

---

## 2. Long-Term Objectives

Develop an application capable of:

- Scanning directories containing photographs and videos.
- Automatically detecting faces within images.
- Generating facial embeddings for each detected face.
- Comparing embeddings to identify recurring individuals.
- Allowing users to assign names to recognised faces.
- Remembering identified individuals between sessions.
- Automatically identifying previously labelled individuals in new photographs.
- Organising photographs into folders according to the people they contain.
- Processing videos to identify individuals appearing in them.
- Providing a simple interface for reviewing and correcting identifications.
- Operating entirely locally without subscription fees or external AI APIs.

The application should preserve original files and avoid destructive changes without user confirmation.

---

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development and file management |
| pathlib | Managing file and directory paths |
| Pillow (PIL) | Reading images and extracting image properties |
| OpenCV | Computer vision library used to execute AI models |
| YuNet | Pretrained face detection model |
| SFace | Pretrained model for generating facial embeddings |
| NumPy | Handling numerical image and embedding data |
| SQLite | Local storage of identified individuals and associated information |

The application uses existing pretrained models rather than training facial recognition models from scratch.

---

## 4. System Architecture

The intended application workflow is:

```text
PHOTO / VIDEO LIBRARY
          |
          v
FILE DISCOVERY
Identify supported files
          |
          v
IMAGE PROCESSING
Load images / video frames
          |
          v
FACE DETECTION
Locate faces using YuNet
          |
          v
FACE EMBEDDINGS
Convert faces into numerical vectors
          |
          v
FACE COMPARISON
Compare against known individuals
          |
          v
PERSON IDENTIFICATION
Recognise or flag unknown faces
          |
          v
LOCAL DATABASE
Store confirmed identities
          |
          v
PHOTO ORGANISATION
Group and file photographs
```

The system separates the process of locating faces from the process of recognising individuals.

### Face Detection

The face detection model identifies where faces appear within photographs.

It returns information about each detected face, including its position within the image.

### Face Recognition

A separate model generates numerical embeddings representing facial features.

Embeddings can be compared to estimate whether two detected faces belong to the same individual.

### Identity Management

Recognised individuals and their associated information are stored locally.

The intended workflow allows users to confirm identities, enabling the application to recognise the same people in future photographs.

### File Organisation

Once individuals have been identified, the application will use this information to organise photographs and videos.

This component has not yet been implemented.

---

## 5. Current Functionality

### File Discovery

The application can:

- Search a specified directory for image files.
- Identify supported file extensions.
- Count files by extension.
- Read image dimensions.
- Create an output directory when required.

### Face Detection

Two face detection approaches have been investigated:

**Haar Cascade Classifier**

Initially used to identify faces within images.

This provided an introduction to traditional computer vision techniques.

Some false-positive detections were observed.

**YuNet**

A pretrained neural-network-based face detector implemented through OpenCV.

YuNet was introduced to improve face detection and investigate a more modern machine-learning approach.

The application can identify faces and retrieve their bounding-box coordinates.

### Visual Debugging

The application can draw rectangles around detected faces and save annotated images to the output directory.

This allows the performance of face detection to be inspected visually.

### Facial Embeddings

Initial work has been undertaken to generate numerical embeddings from detected faces.

An embedding has been successfully generated and inspected.

Example output:

```text
Shape: (1, 128)
Data type: float32
Number of bytes: 512
```

These embeddings will eventually be used to compare and recognise individuals.

### Local Identity Database

Initial work has been undertaken to store and retrieve information about known individuals using a local database.

The database is excluded from GitHub because it may contain personal information.

---

## 6. Project Structure

```text
AI_Photo_Filer/
│
├── main.py
├── README.md
├── .gitignore
│
├── models/
│   └── Pretrained AI models
│
├── test_photos/
│   └── Test photographs
│
├── output_folder/
│   └── Generated debugging images
│
└── known_people
    └── Local identity database
```

### main.py

The main Python application.

Currently contains functions for file discovery, image processing and facial detection, alongside developing facial recognition functionality.

### models/

Stores downloaded pretrained model files used by OpenCV.

### test_photos/

Contains images used during development and testing.

### output_folder/

Stores generated images, including photographs annotated with face detection rectangles.

### known_people

Local database used for identity information.

This file should not be committed to GitHub.

---

## 7. AI Models

The application uses specialised pretrained AI models rather than a large language model.

Unlike ChatGPT or Qwen, these models are designed to perform specific computer vision tasks.

### Face Detection Model

YuNet analyses an image and returns the locations of detected faces.

The model does not identify who the individuals are.

### Face Recognition Model

A separate model converts detected faces into numerical embeddings.

These embeddings allow the application to compare faces mathematically.

Similar embeddings may indicate that two faces belong to the same individual.

However, face recognition is probabilistic, and similarity alone does not guarantee that two faces belong to the same person.

User confirmation and appropriate matching thresholds will therefore be important.

---

## 8. Key Development Concepts

### Pretrained AI Models

AI models can be downloaded and used locally without having to train them.

The model's learned information is encoded in its parameters.

### Computer Vision

Computer vision allows software to extract information from images.

In this application, OpenCV provides the tools required to load images, detect faces and process the results.

### Embeddings

Embeddings are numerical representations of information.

In this project, they represent facial characteristics rather than the semantic meaning of text.

The same underlying concept is also used in applications such as semantic document searching and Retrieval-Augmented Generation (RAG).

### Modular Functions

The application uses Python functions to separate tasks such as finding images, extracting image dimensions and detecting faces.

### Local Data Processing

Photographs, models and identity information can be processed and stored on the user's computer without requiring external AI services.

### Database Management

SQLite provides a lightweight method of storing structured information about identified individuals.

---

## 9. Current Limitations

- Face detection has been implemented, but reliable identification of individuals is still in development.
- Facial embeddings can be generated, but the complete recognition workflow is not yet implemented.
- Matching thresholds have not been established or systematically tested.
- Automatic photograph organisation has not been implemented.
- Video processing has not been implemented.
- Unknown individuals cannot yet be reviewed and labelled through a dedicated interface.
- Recognition accuracy has not been evaluated across different lighting conditions, ages and viewing angles.
- Some face detections may produce false positives.
- The application currently requires interaction through Python rather than a dedicated user interface.

---

## 10. Future Development

### Phase 1 — Facial Recognition

- Complete face embedding generation.
- Compare embeddings between photographs.
- Establish appropriate similarity thresholds.
- Identify recurring individuals.
- Investigate false positives and incorrect matches.

### Phase 2 — Identity Management

- Allow users to assign names to detected individuals.
- Store confirmed face embeddings in SQLite.
- Retrieve known identities when processing new photographs.
- Allow users to correct incorrect identifications.

### Phase 3 — Automatic Photo Organisation

- Scan larger photograph libraries.
- Identify individuals appearing in each photograph.
- Organise photographs into appropriate folders.
- Handle photographs containing multiple individuals.
- Prevent duplicate processing.
- Preserve original photographs.

### Phase 4 — Video Processing

- Extract representative frames from videos.
- Detect and recognise individuals appearing in those frames.
- Associate recognised individuals with video files.
- Avoid unnecessary processing of duplicate or similar frames.

### Phase 5 — User Interface

- Introduce a simple graphical interface.
- Display detected faces and suggested identities.
- Allow users to confirm or correct recognition results.
- Provide controls for organising and exporting photographs.

---

## 11. Project Purpose

This project forms part of an ongoing programme of software and AI development.

Its initial purpose is to develop practical experience with:

- Python programming
- Computer vision
- Pretrained machine-learning models
- Image processing
- Facial detection and recognition
- Numerical embeddings
- Data structures
- Local databases
- File management
- Debugging and testing

The project also provides an introduction to building applications around existing AI models rather than developing the underlying models themselves.

The longer-term objective is to produce a useful, entirely local family photo and video organiser.