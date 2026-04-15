import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var viewModel: BrainSyncViewModel

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    statusCard
                    transcriptCard
                    if !viewModel.quizzes.isEmpty {
                        quizCard
                    }
                    if let feedback = viewModel.feedback {
                        feedbackCard(feedback)
                    }
                }
                .padding(20)
            }
            .navigationTitle("BrainSync v2")
        }
    }

    private var statusCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Hybrid flow")
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(viewModel.status)
                .font(.headline)
            if !viewModel.errorMessage.isEmpty {
                Text(viewModel.errorMessage)
                    .foregroundStyle(.red)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private var transcriptCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Transcript")
                .font(.headline)
            TextEditor(text: $viewModel.transcript)
                .frame(minHeight: 180)
                .padding(8)
                .background(Color.secondary.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))

            HStack {
                Button("Load sample") {
                    viewModel.useSampleTranscript()
                }
                .buttonStyle(.bordered)

                Button("Prepare session") {
                    Task { await viewModel.prepare() }
                }
                .buttonStyle(.borderedProminent)
                .disabled(viewModel.isBusy)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private var quizCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Quiz")
                .font(.headline)

            ForEach(Array(viewModel.quizzes.enumerated()), id: \.offset) { index, quiz in
                VStack(alignment: .leading, spacing: 10) {
                    Text(quiz.category)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(quiz.question)
                        .font(.subheadline.weight(.semibold))

                    ForEach(["A", "B"], id: \.self) { key in
                        Button {
                            viewModel.answers[index] = key
                        } label: {
                            HStack {
                                Text("\(key). \(quiz.options[key] ?? "")")
                                Spacer()
                                if viewModel.answers[index] == key {
                                    Image(systemName: "checkmark.circle.fill")
                                }
                            }
                        }
                        .buttonStyle(.bordered)
                    }
                }
                .padding()
                .background(Color.secondary.opacity(0.06), in: RoundedRectangle(cornerRadius: 16))
            }

            Button("Get feedback") {
                Task { await viewModel.submitFeedback() }
            }
            .buttonStyle(.borderedProminent)
            .disabled(viewModel.isBusy)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func feedbackCard(_ feedback: FeedbackEnvelope) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("What to remember")
                .font(.headline)

            ForEach(feedback.rememberHighlights, id: \.self) { item in
                Text("• \(item)")
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(Color.yellow.opacity(0.14), in: RoundedRectangle(cornerRadius: 14))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }
}
