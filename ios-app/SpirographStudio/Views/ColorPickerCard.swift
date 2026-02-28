import SwiftUI

struct ColorPickerCard: View {
    @Binding var selectedColorIndex: Int
    @Binding var isRainbow: Bool

    var body: some View {
        // 9 items (8 swatches + wand) distributed evenly across full width
        HStack(spacing: 0) {
            ForEach(0..<AppColors.presets.count, id: \.self) { index in
                let isSelected = !isRainbow && selectedColorIndex == index

                Circle()
                    .fill(AppColors.presets[index])
                    .frame(width: Layout.swatchSize, height: Layout.swatchSize)
                    .shadow(color: isSelected
                            ? AppColors.presets[index].opacity(0.75)
                            : .clear,
                            radius: 9)
                    .overlay {
                        if isSelected {
                            Circle().stroke(Color.white, lineWidth: 2)
                        }
                    }
                    .scaleEffect(isSelected ? 1.12 : 1.0)
                    .opacity(isRainbow ? 0.4 : 1.0)
                    .animation(.spring(response: 0.22, dampingFraction: 0.65), value: isSelected)
                    .animation(.easeInOut(duration: 0.2), value: isRainbow)
                    .frame(maxWidth: .infinity)
                    .onTapGesture {
                        guard !isRainbow else { return }
                        selectedColorIndex = index
                        let gen = UISelectionFeedbackGenerator()
                        gen.prepare()
                        gen.selectionChanged()
                    }
            }

            // Rainbow wand — same equal width slot
            Button {
                isRainbow.toggle()
                let gen = UISelectionFeedbackGenerator()
                gen.prepare()
                gen.selectionChanged()
            } label: {
                ZStack {
                    Circle()
                        .fill(isRainbow
                              ? Color(red: 0.388, green: 0.400, blue: 0.945).opacity(0.7)
                              : Color(white: 0.20))
                        .frame(width: Layout.swatchSize, height: Layout.swatchSize)
                        .shadow(color: isRainbow
                                ? Color(red: 0.388, green: 0.400, blue: 0.945).opacity(0.6)
                                : .clear,
                                radius: 9)
                        .overlay {
                            if isRainbow {
                                Circle().stroke(Color.white, lineWidth: 2)
                            }
                        }
                    Image(systemName: "wand.and.sparkles")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(.white)
                }
                .scaleEffect(isRainbow ? 1.12 : 1.0)
                .animation(.spring(response: 0.22, dampingFraction: 0.65), value: isRainbow)
            }
            .buttonStyle(.plain)
            .frame(maxWidth: .infinity)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
    }
}
