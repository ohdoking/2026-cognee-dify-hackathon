import Foundation
import SwiftUI

@MainActor
final class BrainSyncViewModel: ObservableObject {
    @Published var transcript: String = ""
    @Published var preparedSession: PreparedSession?
    @Published var quizzes: [QuizItem] = []
    @Published var answers: [Int: String] = [:]
    @Published var feedback: FeedbackEnvelope?
    @Published var isBusy = false
    @Published var status = "Ready"
    @Published var errorMessage = ""

    private let api = APIClient()
    private let gemma: LocalGemmaQuizGenerating = PreviewGemmaQuizGenerator()

    func useSampleTranscript() {
        transcript = """
        Marcus: Hey team, we only have 2 hours left. I just found a great designer who can join us right now and fix our UI.
        User: Sounds good. Let's add them immediately.
        Dokeun: Let's also make the repository private for a few hours.
        User: Okay, I agree.
        """
    }

    func prepare() async {
        guard !transcript.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        isBusy = true
        errorMessage = ""
        status = "Syncing with Cognee..."
        defer { isBusy = false }

        do {
            let prepared = try await api.prepareSession(transcript: transcript)
            preparedSession = prepared
            status = "Generating quiz with local Gemma..."
            quizzes = try await gemma.generateQuizzes(from: prepared)
            status = "Quiz ready"
        } catch {
            errorMessage = error.localizedDescription
            status = "Failed"
        }
    }

    func submitFeedback() async {
        guard !quizzes.isEmpty else { return }
        isBusy = true
        errorMessage = ""
        status = "Loading Cognee feedback..."
        defer { isBusy = false }

        do {
            feedback = try await api.feedback(transcript: transcript, quizzes: quizzes, userAnswers: answers)
            status = "Review ready"
        } catch {
            errorMessage = error.localizedDescription
            status = "Failed"
        }
    }
}
