import SwiftUI

struct SlidersCard: View {
    @Binding var sliderR: Double
    @Binding var sliderr: Double
    @Binding var sliderd: Double
    @Binding var sliderSpeed: Double
    @Binding var sliderWidth: Double

    var body: some View {
        VStack(spacing: 4) {
            SpiroSliderView(sfSymbol: "circle.dashed", label: "Big Circle (R)",
                            value: $sliderR, minValue: 50, maxValue: 300,
                            accentColor: AppColors.sliderR)

            SpiroSliderView(sfSymbol: "gearshape.fill", label: "Little Wheel (r)",
                            value: $sliderr, minValue: 5, maxValue: 200,
                            accentColor: AppColors.sliderr)

            SpiroSliderView(sfSymbol: "pencil.tip", label: "Pen Reach (d)",
                            value: $sliderd, minValue: 5, maxValue: 250,
                            accentColor: AppColors.sliderd)

            SpiroSliderView(sfSymbol: "bolt.fill", label: "Speed",
                            value: $sliderSpeed, minValue: 1, maxValue: 20,
                            accentColor: AppColors.sliderSpeed)

            SpiroSliderView(sfSymbol: "lineweight", label: "Line Width",
                            value: $sliderWidth, minValue: 1, maxValue: 8,
                            accentColor: AppColors.sliderWidth)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
    }
}
