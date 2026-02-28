import UIKit
import Combine

@MainActor
final class DrawingEngine: ObservableObject {

    // MARK: - Published State

    @Published private(set) var canvasImage: UIImage
    @Published private(set) var isDrawing: Bool = false
    @Published private(set) var drawProgress: Double = 0.0  // 0.0 – 1.0
    @Published private(set) var layerCount: Int = 0
    @Published private(set) var undoCount: Int = 0

    // MARK: - Private State

    private var undoStack: [UIImage] = []
    private let maxUndo = 20
    private var drawPoints: [CGPoint] = []
    private var drawIndex: Int = 0
    private var drawTimer: Timer?
    private var pendingR: Double = 150
    private var pendingr: Double = 80
    private var pendingd: Double = 100
    private var pendingColorMode: ColorMode = .solid(UIColor.white)
    private var pendingLineWidth: Double = 1
    private var pendingSpeed: Int = 5

    let canvasSize: CGFloat

    // MARK: - Init

    init(canvasSize: CGFloat) {
        self.canvasSize = canvasSize
        self.canvasImage = DrawingEngine.makeBackground(size: CGSize(width: canvasSize, height: canvasSize))
    }

    // MARK: - Background

    static func makeBackground(size: CGSize) -> UIImage {
        UIGraphicsBeginImageContextWithOptions(size, true, 1.0)
        defer { UIGraphicsEndImageContext() }

        guard let ctx = UIGraphicsGetCurrentContext() else {
            return UIImage()
        }

        // Dark navy base
        ctx.setFillColor(UIColor(red: 0.047, green: 0.047, blue: 0.094, alpha: 1).cgColor)
        ctx.fill(CGRect(origin: .zero, size: size))

        // Dot grid
        let spacing: CGFloat = 28
        let dotRadius: CGFloat = 1.2
        let cx = size.width / 2
        let cy = size.height / 2

        let cols = Int(size.width / spacing) + 2
        let rows = Int(size.height / spacing) + 2

        for row in 0..<rows {
            for col in 0..<cols {
                let x = CGFloat(col) * spacing
                let y = CGFloat(row) * spacing

                // Distance from center for vignette
                let dx = x - cx
                let dy = y - cy
                let dist = sqrt(dx * dx + dy * dy)
                let maxDist = sqrt(cx * cx + cy * cy)
                let centerFactor = 1.0 - dist / maxDist * 0.4  // 0.6 – 1.0

                // Slight brightness variation per dot
                let variation = CGFloat.random(in: -0.08...0.08)
                let brightness = (0.28 + variation) * centerFactor

                ctx.setFillColor(UIColor(red: 0.20, green: 0.22, blue: 0.34 + variation * 0.1, alpha: brightness).cgColor)
                let dotRect = CGRect(x: x - dotRadius, y: y - dotRadius,
                                     width: dotRadius * 2, height: dotRadius * 2)
                ctx.fillEllipse(in: dotRect)
            }
        }

        return UIGraphicsGetImageFromCurrentImageContext() ?? UIImage()
    }

    // MARK: - Drawing

    func startDrawing(R: Double, r: Double, d: Double,
                      speed: Int, lineWidth: Double, colorMode: ColorMode) {
        if isDrawing {
            stopDrawing()
            return
        }

        pushUndo()

        let rawPoints = SpiroMath.computePoints(R: R, r: r, d: d)
        drawPoints = SpiroMath.scalePoints(rawPoints, canvasSize: canvasSize, margin: 28)
        drawIndex = 1
        isDrawing = true
        drawProgress = 0
        layerCount += 1

        pendingR = R
        pendingr = r
        pendingd = d
        pendingColorMode = colorMode
        pendingLineWidth = lineWidth
        pendingSpeed = max(1, speed)

        drawTimer = Timer.scheduledTimer(withTimeInterval: 1.0 / 60.0, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                self?.stepDraw()
            }
        }
        RunLoop.main.add(drawTimer!, forMode: .common)
    }

    private func stepDraw() {
        guard isDrawing, drawIndex < drawPoints.count else {
            finishDrawing()
            return
        }

        let end = min(drawIndex + pendingSpeed, drawPoints.count)
        let total = drawPoints.count

        UIGraphicsBeginImageContextWithOptions(
            CGSize(width: canvasSize, height: canvasSize), true, 1.0)
        canvasImage.draw(at: .zero)

        guard let ctx = UIGraphicsGetCurrentContext() else {
            UIGraphicsEndImageContext()
            return
        }

        ctx.setLineWidth(CGFloat(pendingLineWidth))
        ctx.setLineCap(.round)
        ctx.setLineJoin(.round)

        for i in drawIndex..<end where i < drawPoints.count {
            let color = pendingColorMode.resolvedColor(index: i, total: total)
            ctx.setStrokeColor(color.cgColor)
            ctx.move(to: drawPoints[i - 1])
            ctx.addLine(to: drawPoints[i])
            ctx.strokePath()
        }

        if let result = UIGraphicsGetImageFromCurrentImageContext() {
            canvasImage = result
        }
        UIGraphicsEndImageContext()

        drawIndex = end
        drawProgress = Double(drawIndex) / Double(max(total - 1, 1))
    }

    private func finishDrawing() {
        drawTimer?.invalidate()
        drawTimer = nil
        isDrawing = false
        drawProgress = 0.0

        // Light haptic on natural completion
        let gen = UIImpactFeedbackGenerator(style: .light)
        gen.prepare()
        gen.impactOccurred()
    }

    func stopDrawing() {
        drawTimer?.invalidate()
        drawTimer = nil
        isDrawing = false
        drawProgress = 0
    }

    // MARK: - Undo

    func pushUndo() {
        undoStack.append(canvasImage)
        if undoStack.count > maxUndo {
            undoStack.removeFirst()
        }
        undoCount = undoStack.count
    }

    func undo() {
        guard !undoStack.isEmpty else { return }
        stopDrawing()
        canvasImage = undoStack.removeLast()
        layerCount = max(0, layerCount - 1)
        undoCount = undoStack.count

        let gen = UIImpactFeedbackGenerator(style: .soft)
        gen.prepare()
        gen.impactOccurred()
    }

    func clear() {
        pushUndo()
        canvasImage = DrawingEngine.makeBackground(size: CGSize(width: canvasSize, height: canvasSize))
        layerCount = 0

        let gen = UIImpactFeedbackGenerator(style: .rigid)
        gen.prepare()
        gen.impactOccurred()
    }

    var canUndo: Bool { !undoStack.isEmpty }
}
