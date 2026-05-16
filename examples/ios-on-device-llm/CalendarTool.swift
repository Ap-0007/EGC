import Foundation
import FoundationModels

struct CalendarCheckTool: Tool {
    let name = "check_calendar_availability"
    let description = "Checks if the user is busy at a specific time."

    @Generable
    struct Arguments {
        var date: Date
    }

    func call(arguments: Arguments) async throws -> ToolOutput {
        // Mocking a calendar check
        let isBusy = Bool.random()
        return .string(isBusy ? "User is busy at this time." : "User is free.")
    }
}
