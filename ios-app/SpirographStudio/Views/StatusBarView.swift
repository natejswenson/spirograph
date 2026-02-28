import SwiftUI

struct StatusBarView: View {
    @ObservedObject var engine: DrawingEngine
    let R: Double
    let r: Double
    let d: Double
    let showSaved: Bool

    private var statusText: String {
        if showSaved {
            return "✓ Saved  ·  \(engine.layerCount) layers"
        }
        if engine.isDrawing {
            let pct = Int(engine.drawProgress * 100)
            return "R=\(Int(R))  r=\(Int(r))  d=\(Int(d))  ·  Drawing \(pct)%  ·  \(engine.layerCount) layers"
        }
        return "R=\(Int(R))  r=\(Int(r))  d=\(Int(d))  ·  \(engine.layerCount) layers  ·  undo: \(engine.undoCount)"
    }

    var body: some View {
        Text(statusText)
            .font(AppFonts.status)
            .foregroundColor(AppColors.statusText)
            .frame(maxWidth: .infinity, alignment: .center)
            .frame(height: 28)
            .padding(.horizontal, 16)
    }
}
