# FacultyIQ File Storage Architecture

## 📦 Overview

FacultyIQ uses **MinIO S3 Object Storage** for storing candidate resumes, publication PDFs, interview recordings, and avatar profile images. The storage subsystem is fully decoupled behind the `IStorageService` and `IBucketManager` abstractions to support future cloud migration (AWS S3, Azure Blob Storage) seamlessly.

---

## 🪣 Bucket Taxonomy

| Bucket Name | Purpose | Retention / Access Policy |
| :--- | :--- | :--- |
| `facultyiq-resumes` | Candidate CVs, academic transcripts, research dossiers | Private / Encrypted |
| `facultyiq-videos` | Recorded automated interviews and presentation files | Private / Presigned URL |
| `facultyiq-profiles` | User profile avatars and institutional logos | Public-Read / CDN Ready |
| `facultyiq-temp` | Temporary processing files for PDF extraction & OCR | Ephemeral / Auto-purge |

---

## 🛠 Features

- **Streaming Upload & Download**: Memory-efficient stream operations without loading entire files into memory.
- **Presigned URLs**: Secure, time-limited direct downloads for large media files (default 1-hour expiry).
- **MIME & Content Validation**: Enforces strict file extension whitelists and file size upper bounds.
- **Health Checks**: `MinioHealthCheck` continuously monitors object store connectivity and bucket availability.
