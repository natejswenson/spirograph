import SwiftUI

struct ColorPickerCard: View {
    @Binding var selectedColorIndex: Int
    @Binding var isRainbow: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            // Section header
            Text("DRAW COLOR")
                .font(AppFonts.sectionHeader)
                .foregroundColor(AppColors.statusText)

            // Color swatches
            HStack(spacing: Layout.swatchGap) {
                ForEach(0..<AppColors.presets.count, id: \.self) { index in
                    let isSelected = selectedColorIndex == index

                    RoundedRectangle(cornerRadius: Layout.swatchRadius)
                        .fill(AppColors.presets[index])
                        .frame(width: Layout.swatchSize, height: Layout.swatchSize)
                        .overlay {
                            if isSelected {
                                RoundedRectangle(cornerRadius: Layout.swatchRadius)
                                    .stroke(Color.white, lineWidth: 3)
                            }
                        }
                        .scaleEffect(isSelected ? 1.15 : 1.0)
                        .opacity(isRainbow ? 0.5 : 1.0)
                        .animation(.spring(response: 0.25), value: isSelected)
                        .animation(.easeInOut(duration: 0.2), value: isRainbow)
                        .onTapGesture {
                            guard !isRainbow else { return }
                            selectedColorIndex = index

                            let gen = UISelectionFeedbackGenerator()
                            gen.prepare()
                            gen.selectionChanged()
                        }
                }
                Spacer()
            }

            // Rainbow toggle
            Toggle(isOn: $isRainbow) {
                HStack(spacing: 6) {
                    Text("🌈")
                        .font(.system(size: 16))
                    Text("Rainbow")
                        .font(AppFonts.sliderLabel)
                        .foregroundColor(.white.opacity(0.85))
                }
            }
            .toggleStyle(SpiroToggleStyle())
        }
        .padding(Layout.cardPadding)
        .background(AppColors.panel)
        .clipShape(RoundedRectangle(cornerRadius: Layout.cardRadius))
    }
}

// MARK: - Custom Toggle Style

struct SpiroToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack {
            configuration.label
            Spacer()
            ZStack {
                Capsule()
                    .fill(configuration.isOn
                          ? Color(red: 0.388, green: 0.400, blue: 0.945).opacity(0.8)
                          : Color(white: 0.25))
                    .frame(width: 44, height: 26)

                Circle()
                    .fill(Color.white)
                    .frame(width: 20, height: 20)
                    .offset(x: configuration.isOn ? 9 : -9)
                    .animation(.spring(response: 0.3, dampingFraction: 0.7), value: configuration.isOn)
            }
            .onTapGesture {
                configuration.isOn.toggle()
            }
        }
    }
}
