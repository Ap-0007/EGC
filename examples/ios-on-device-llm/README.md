# iOS 26 FoundationModels Example

This example demonstrates how to integrate Apple's on-device LLM into a SwiftUI application using the `FoundationModels` framework (iOS 26+).

## Features
- **Availability Checks:** Ensures the device and settings are ready for Apple Intelligence.
- **Structured Output:** Uses `@Generable` to extract typed `UserTask` objects from natural language.
- **Tool Calling:** Implements a `CalendarCheckTool` that the model can invoke to verify availability.
- **Privacy-First:** All processing happens on-device; no data is sent to the cloud.

## Key Files
- `TaskModel.swift`: Defines the `@Generable` structured data type.
- `CalendarTool.swift`: Implements a custom tool for the LLM.
- `ContentView.swift`: Main UI with model lifecycle management.

## Requirements
- Xcode 17+ (Targeting iOS 26)
- Device with Apple Intelligence support
