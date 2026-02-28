import SwiftUI

/// Bottom-sheet style controls panel — fixed 290pt height, no scroll.
/// Budget: 16 (pill) + 138 (sliders) + 1 (div) + 38 (colors) + 1 (div) + 96 (buttons) = 290pt
struct ControlsPanelView: View {
    @Binding var sliderR: Double
    @Binding var sliderr: Double
    @Binding var sliderd: Double
    @Binding var sliderSpeed: Double
    @Binding var sliderWidth: Double
    @Binding var selectedColorIndex: Int
    @Binding var isRainbow: Bool

    @ObservedObject var engine: DrawingEngine

    let onDraw: () -> Void
    let onUndo: () -> Void
    let onClear: () -> Void
    let onRandom: () -> Void
    let onSave: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            // Pull indicator — 16pt
            pullIndicator

            // Sliders section — 138pt
            SlidersCard(
                sliderR: $sliderR,
                sliderr: $sliderr,
                sliderd: $sliderd,
                sliderSpeed: $sliderSpeed,
                sliderWidth: $sliderWidth
            )

            sectionDivider

            // Color row — 38pt
            ColorPickerCard(
                selectedColorIndex: $selectedColorIndex,
                isRainbow: $isRainbow
            )

            sectionDivider

            // Buttons section — 96pt
            ButtonsCard(
                engine: engine,
                onDraw: onDraw,
                onUndo: onUndo,
                onClear: onClear,
                onRandom: onRandom,
                onSave: onSave
            )
        }
        .background {
            ZStack {
                RoundedRectangle(cornerRadius: Layout.panelRadius, style: .continuous)
                    .fill(.ultraThinMaterial)
                RoundedRectangle(cornerRadius: Layout.panelRadius, style: .continuous)
                    .fill(LinearGradient(
                        colors: [AppColors.glassHighlight, .clear],
                        startPoint: .top, endPoint: .center))
            }
        }
        .overlay {
            RoundedRectangle(cornerRadius: Layout.panelRadius, style: .continuous)
                .stroke(AppColors.glassBorder, lineWidth: 1)
        }
        .shadow(color: .black.opacity(0.5), radius: 24, y: -6)
    }

    private var pullIndicator: some View {
        RoundedRectangle(cornerRadius: 3)
            .fill(Color.white.opacity(0.30))
            .frame(width: 42, height: 5)
            .frame(maxWidth: .infinity)
            .frame(height: 16)
    }

    private var sectionDivider: some View {
        LinearGradient(
            colors: [.clear, AppColors.glassBorder, AppColors.glassBorder, .clear],
            startPoint: .leading, endPoint: .trailing)
            .frame(height: 1)
    }
}
