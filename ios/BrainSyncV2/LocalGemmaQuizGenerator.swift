import Foundation

protocol LocalGemmaQuizGenerating {
    func generateQuizzes(from preparedSession: PreparedSession) async throws -> [QuizItem]
}

struct LocalGemmaQuizGenerator: LocalGemmaQuizGenerating {
    func generateQuizzes(from preparedSession: PreparedSession) async throws -> [QuizItem] {
        throw NSError(
            domain: "BrainSyncV2",
            code: -1,
            userInfo: [
                NSLocalizedDescriptionKey:
                    "Hook your local Gemma 4 runtime here. Use preparedSession.gemmaPrompt as the local prompt package."
            ]
        )
    }
}

struct PreviewGemmaQuizGenerator: LocalGemmaQuizGenerating {
    func generateQuizzes(from preparedSession: PreparedSession) async throws -> [QuizItem] {
        return [
            QuizItem(
                category: "Rule Recall",
                question: "Is making the repository private guaranteed to be safe under the event rules?",
                options: ["A": "Yes", "B": "No"],
                correct_answer: "B",
                insight: "Submission visibility rules must be checked explicitly before hiding the repository."
            ),
            QuizItem(
                category: "Time Limit",
                question: "Did the official rules change the demo limit to 10 minutes?",
                options: ["A": "No", "B": "Yes"],
                correct_answer: "A",
                insight: "Hallway rumors are not the same as official guidance."
            )
        ]
    }
}
