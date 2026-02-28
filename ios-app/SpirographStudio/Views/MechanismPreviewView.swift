import SwiftUI

struct MechanismPreviewView: View {
    let R: Double
    let r: Double
    let d: Double
    let isDrawing: Bool
    let selectedColor: Color

    @State private var theta: Double = 0

    var body: some View {
        TimelineView(.animation) { timeline in
            Canvas { context, size in
                let sz = min(size.width, size.height)
                let scale = sz / 2 * 0.82
                let R_px = scale
                let rRaw = min(r, R - 1)
                let r_px = R_px * CGFloat(rRaw / R)
                let d_px = R_px * CGFloat(d / R)
                let center = CGPoint(x: size.width / 2, y: size.height / 2)

                // Wheel center position
                let wheelCenterX = center.x + (R_px - r_px) * cos(theta)
                let wheelCenterY = center.y + (R_px - r_px) * sin(theta)
                let wheelCenter = CGPoint(x: wheelCenterX, y: wheelCenterY)

                // Pen angle (rolling constraint)
                let penAngle = -(R_px - r_px) / max(r_px, 1) * theta
                let penX = wheelCenterX + d_px * cos(penAngle)
                let penY = wheelCenterY + d_px * sin(penAngle)
                let penPos = CGPoint(x: penX, y: penY)

                // 1. Ghost trace (900 steps, low opacity)
                drawGhostTrace(context: context, center: center, scale: scale,
                               R: R, r: rRaw, d: d, color: selectedColor)

                // 2. Outer ring
                var outerPath = Path()
                outerPath.addEllipse(in: CGRect(x: center.x - R_px, y: center.y - R_px,
                                                width: R_px * 2, height: R_px * 2))
                context.stroke(outerPath,
                               with: .color(AppColors.sliderR),
                               lineWidth: 2)

                // 3. Tick marks (12, every 30 degrees)
                for tick in 0..<12 {
                    let angle = Double(tick) * .pi / 6
                    let innerR = R_px - 5
                    let p1 = CGPoint(x: center.x + R_px * cos(angle),
                                     y: center.y + R_px * sin(angle))
                    let p2 = CGPoint(x: center.x + innerR * cos(angle),
                                     y: center.y + innerR * sin(angle))
                    var tickPath = Path()
                    tickPath.move(to: p1)
                    tickPath.addLine(to: p2)
                    context.stroke(tickPath, with: .color(AppColors.sliderR.opacity(0.5)), lineWidth: 1)
                }

                // 4. Inner wheel (semi-transparent fill + stroke)
                let wheelRect = CGRect(x: wheelCenterX - r_px, y: wheelCenterY - r_px,
                                       width: r_px * 2, height: r_px * 2)
                var wheelPath = Path()
                wheelPath.addEllipse(in: wheelRect)
                context.fill(wheelPath, with: .color(AppColors.sliderr.opacity(0.3)))
                context.stroke(wheelPath, with: .color(AppColors.sliderr), lineWidth: 2)

                // 5. Gear dots on wheel perimeter (4-8 dots)
                let dotCount = max(4, min(8, Int(r_px / 8)))
                for i in 0..<dotCount {
                    let gearAngle = theta + Double(i) * 2 * .pi / Double(dotCount)
                    let gx = wheelCenterX + r_px * cos(gearAngle)
                    let gy = wheelCenterY + r_px * sin(gearAngle)
                    var dotPath = Path()
                    dotPath.addEllipse(in: CGRect(x: gx - 2, y: gy - 2, width: 4, height: 4))
                    context.fill(dotPath, with: .color(AppColors.sliderr))
                }

                // 6. Crosshair through wheel center
                let crosshairLen: CGFloat = 4
                let crossColor = Color(red: 0.4, green: 0.3, blue: 0.7)
                var crossH = Path()
                crossH.move(to: CGPoint(x: wheelCenterX - crosshairLen, y: wheelCenterY))
                crossH.addLine(to: CGPoint(x: wheelCenterX + crosshairLen, y: wheelCenterY))
                context.stroke(crossH, with: .color(crossColor), lineWidth: 1)
                var crossV = Path()
                crossV.move(to: CGPoint(x: wheelCenterX, y: wheelCenterY - crosshairLen))
                crossV.addLine(to: CGPoint(x: wheelCenterX, y: wheelCenterY + crosshairLen))
                context.stroke(crossV, with: .color(crossColor), lineWidth: 1)

                // 7. Pen arm
                var armPath = Path()
                armPath.move(to: wheelCenter)
                armPath.addLine(to: penPos)
                context.stroke(armPath, with: .color(AppColors.sliderd.opacity(0.8)), lineWidth: 1.5)

                // 8. Pen dot (3 concentric circles)
                let penColor = selectedColor
                var outer = Path()
                outer.addEllipse(in: CGRect(x: penX - 5, y: penY - 5, width: 10, height: 10))
                context.fill(outer, with: .color(penColor.opacity(0.9)))

                var middle = Path()
                middle.addEllipse(in: CGRect(x: penX - 3, y: penY - 3, width: 6, height: 6))
                context.fill(middle, with: .color(.white))

                var inner = Path()
                inner.addEllipse(in: CGRect(x: penX - 2, y: penY - 2, width: 4, height: 4))
                context.fill(inner, with: .color(penColor))

                // 9. Labels
                let labelStyle = AttributedString("R=\(Int(R))", attributes: AttributeContainer()
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(AppColors.statusText))
                context.draw(Text(labelStyle), at: CGPoint(x: 8, y: 6), anchor: .topLeading)

                let rLabelStyle = AttributedString("r=\(Int(rRaw))", attributes: AttributeContainer()
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(AppColors.statusText))
                context.draw(Text(rLabelStyle), at: CGPoint(x: size.width - 8, y: 6), anchor: .topTrailing)
            }
            .onChange(of: timeline.date) { _, _ in
                let increment = isDrawing ? 0.055 : 0.018
                theta += increment
                if theta > 2 * .pi * 100 { theta = 0 }
            }
        }
    }

    private func drawGhostTrace(context: GraphicsContext, center: CGPoint,
                                 scale: CGFloat, R: Double, r: Double, d: Double, color: Color) {
        let pts = SpiroMath.computeGhostPoints(R: R, r: r, d: d, steps: 900)
        guard pts.count > 1 else { return }

        var maxExtent: CGFloat = 1
        for p in pts {
            let e = max(abs(p.x), abs(p.y))
            if e > maxExtent { maxExtent = e }
        }
        let drawScale = scale / maxExtent

        var path = Path()
        for (i, p) in pts.enumerated() {
            let sp = CGPoint(x: center.x + p.x * drawScale, y: center.y + p.y * drawScale)
            if i == 0 { path.move(to: sp) } else { path.addLine(to: sp) }
        }
        path.closeSubpath()
        context.stroke(path, with: .color(color.opacity(0.1)), lineWidth: 1)
    }
}
