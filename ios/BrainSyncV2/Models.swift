import Foundation

struct PreparedSession: Decodable {
    let transcript: String
    let datasetName: String
    let contexts: [String]
    let analysisQuery: String
    let gemmaPrompt: String
}

struct QuizEnvelope: Codable {
    let quizzes: [QuizItem]
}

struct QuizItem: Codable, Identifiable {
    let id = UUID()
    let category: String
    let question: String
    let options: [String: String]
    let correct_answer: String
    let insight: String

    enum CodingKeys: String, CodingKey {
        case category
        case question
        case options
        case correct_answer
        case insight
    }
}

struct FeedbackEnvelope: Decodable {
    let datasetName: String
    let items: [FeedbackItem]
    let rememberHighlights: [String]
}

struct FeedbackItem: Decodable, Identifiable {
    let id = UUID()
    let index: Int?
    let query: String?
    let contexts: [String]?
    let error: String?
    let comparison: FeedbackComparison?

    enum CodingKeys: String, CodingKey {
        case index
        case query
        case contexts
        case error
        case comparison
    }
}

struct FeedbackComparison: Decodable {
    let rememberedCorrectly: Bool
    let userAnswer: String
    let correctAnswer: String
}
