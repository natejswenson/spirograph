import SwiftUI

struct SlidersCard: View {
    @Binding var sliderR: Double
    @Binding var sliderr: Double
    @Binding var sliderd: Double
    @Binding var sliderSpeed: Double
    @Binding var sliderWidth: Double

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Section header
            Text("PARAMETERS")
                .font(AppFonts.sectionHeader)
                .foregroundColor(AppColors.statusText)
                .padding(.bottom, 6)

            SpiroSliderView(emoji: "⭕", label: "Big Circle (R)",
                            value: $sliderR, minValue: 50, maxValue: 300,
                            accentColor: AppColors.sliderR)

            Divider().background(AppColors.cardBorder).padding(.vertical, 2)

            SpiroSliderView(emoji: "🔵", label: "Little Wheel (r)",
                            value: $sliderr, minValue: 5, maxValue: 200,
                            accentColor: AppColors.sliderr)

            Divider().background(AppColors.cardBorder).padding(.vertical, 2)

            SpiroSliderView(emoji: "✏️", label: "Pen Reach (d)",
                            value: $sliderd, minValue: 5, maxValue: 250,
                            accentColor: AppColors.sliderd)

            Divider().background(AppColors.cardBorder).padding(.vertical, 2)

            SpiroSliderView(emoji: "⚡", label: "Speed",
                            value: $sliderSpeed, minValue: 1, maxValue: 20,
                            accentColor: AppColors.sliderSpeed)

            Divider().background(AppColors.cardBorder).padding(.vertical, 2)

            SpiroSliderView(emoji: "📏", label: "Line Width",
                            value: $sliderWidth, minValue: 1, maxValue: 8,
                            accentColor: AppColors.sliderWidth)
        }
        .padding(Layout.cardPadding)
        .background(AppColors.panel)
        .clipShape(RoundedRectangle(cornerRadius: Layout.cardRadius))
    }
}
