import SwiftUI

@main
struct BrainSyncV2App: App {
    @StateObject private var viewModel = BrainSyncViewModel()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(viewModel)
        }
    }
}
