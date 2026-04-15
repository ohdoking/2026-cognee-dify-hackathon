# BrainSync iOS v2

This folder contains a SwiftUI app scaffold for the Cognee + local Gemma hybrid flow.

Current architecture:

- iPhone records audio or imports a file
- `/api/v2/transcribe` creates the transcript
- `/api/v2/session/prepare` syncs/searches Cognee and returns a Gemma prompt package
- a local Gemma adapter generates quizzes on-device
- `/api/v2/session/feedback` returns Cognee-backed review feedback

Important note:

- Google AI Edge Gallery demonstrates that Gemma can run locally on iPhone, but this repo currently provides a pluggable local adapter interface rather than a direct AI Edge Gallery SDK integration.
- Replace `LocalGemmaQuizGenerator` with your preferred on-device runtime bridge.

Suggested Xcode setup:

1. Create a new iOS App project in Xcode named `BrainSyncV2`
2. Copy the files from `ios/BrainSyncV2/`
3. Set minimum iOS version to 17+
4. Add microphone permission and speech description strings if you extend local transcription
