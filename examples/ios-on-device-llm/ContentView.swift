import SwiftUI
import FoundationModels

struct ContentView: View {
    private var model = SystemLanguageModel.default
    @State private var input: String = ""
    @State private var extractedTask: UserTask?
    @State private var isProcessing = false
    @State private var errorMessage: String?

    // Initialize session with instructions and tools
    private var session = LanguageModelSession(
        instructions: "You are a smart task assistant. Extract tasks and check availability.",
        tools: [CalendarCheckTool()]
    )

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // 1. Availability Check
                availabilityHeader

                if model.availability == .available {
                    mainInterface
                } else {
                    unavailabilityView
                }
                
                Spacer()
            }
            .padding()
            .navigationTitle("On-Device Task AI")
        }
    }

    private var availabilityHeader: some View {
        HStack {
            Circle()
                .fill(model.availability == .available ? .green : .red)
                .frame(width: 10, height: 10)
            Text(model.availability == .available ? "Apple Intelligence Ready" : "AI Unavailable")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    private var mainInterface: some View {
        VStack(alignment: .leading, spacing: 16) {
            TextField("What needs to be done?", text: $input, axis: .vertical)
                .textFieldStyle(.roundedBorder)
                .lineLimit(3)
            
            Button {
                processInput()
            } label: {
                HStack {
                    if isProcessing { ProgressView().tint(.white) }
                    Text("Extract Task")
                }
                .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .disabled(input.isEmpty || isProcessing)

            if let task = extractedTask {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Extracted Result").font(.headline)
                    Text("Title: \(task.title)")
                    if let date = task.dueDate {
                        Text("Due: \(date.formatted())")
                    }
                    Text("Priority: \(task.priority == 3 ? "High" : (task.priority == 2 ? "Medium" : "Low"))")
                }
                .padding()
                .background(Color.secondary.opacity(0.1))
                .cornerRadius(8)
            }

            if let error = errorMessage {
                Text(error)
                    .foregroundStyle(.red)
                    .font(.caption)
            }
        }
    }

    private var unavailabilityView: some View {
        ContentUnavailableView {
            Label("Model Not Ready", systemImage: "brain.slash")
        } description: {
            Text("Please ensure Apple Intelligence is enabled in Settings and the model has finished downloading.")
        }
    }

    private func processInput() {
        isProcessing = true
        errorMessage = nil
        
        Task {
            do {
                // 2. Structured Response using @Generable
                let response = try await session.respond(
                    to: "Process this task: \(input)",
                    generating: UserTask.self
                )
                
                // 3. Access structured content
                await MainActor.run {
                    self.extractedTask = response.content
                    self.isProcessing = false
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = "Error: \(error.localizedDescription)"
                    self.isProcessing = false
                }
            }
        }
    }
}
