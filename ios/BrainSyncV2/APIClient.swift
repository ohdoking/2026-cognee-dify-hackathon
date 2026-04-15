import Foundation

final class APIClient {
    let baseURL: URL

    init(baseURL: URL = URL(string: "http://127.0.0.1:8000")!) {
        self.baseURL = baseURL
    }

    func transcribe(audioData: Data, filename: String) async throws -> String {
        let boundary = UUID().uuidString
        var request = URLRequest(url: baseURL.appendingPathComponent("api/v2/transcribe"))
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.httpBody = multipartBody(boundary: boundary, filename: filename, mimeType: "audio/wav", data: audioData)

        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response, data: data)
        let payload = try JSONDecoder().decode([String: String].self, from: data)
        return payload["transcript"] ?? ""
    }

    func prepareSession(transcript: String) async throws -> PreparedSession {
        var request = URLRequest(url: baseURL.appendingPathComponent("api/v2/session/prepare"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(["transcript": transcript])

        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response, data: data)
        return try JSONDecoder().decode(PreparedSession.self, from: data)
    }

    func feedback(transcript: String, quizzes: [QuizItem], userAnswers: [Int: String]) async throws -> FeedbackEnvelope {
        let body = FeedbackRequest(transcript: transcript, quizzes: quizzes, user_answers: userAnswers)
        var request = URLRequest(url: baseURL.appendingPathComponent("api/v2/session/feedback"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)

        let (data, response) = try await URLSession.shared.data(for: request)
        try validate(response: response, data: data)
        return try JSONDecoder().decode(FeedbackEnvelope.self, from: data)
    }

    private func validate(response: URLResponse, data: Data) throws {
        guard let http = response as? HTTPURLResponse else { return }
        guard (200..<300).contains(http.statusCode) else {
            let message = String(data: data, encoding: .utf8) ?? "Request failed"
            throw NSError(domain: "BrainSyncV2", code: http.statusCode, userInfo: [NSLocalizedDescriptionKey: message])
        }
    }

    private func multipartBody(boundary: String, filename: String, mimeType: String, data: Data) -> Data {
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        body.append(data)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        return body
    }
}

private struct FeedbackRequest: Codable {
    let transcript: String
    let quizzes: [QuizItem]
    let user_answers: [Int: String]
}
