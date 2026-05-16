import Foundation
import FoundationModels

@Generable(description: "A task extracted from natural language")
struct UserTask {
    var title: String
    
    @Guide(description: "The due date if mentioned, otherwise null")
    var dueDate: Date?
    
    @Guide(description: "Priority level", .range(1...3))
    var priority: Int // 1: Low, 2: Medium, 3: High
}
