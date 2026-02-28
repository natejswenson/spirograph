import CoreGraphics
import Foundation

enum SpiroMath {

    // MARK: - GCD

    static func gcd(_ a: Int, _ b: Int) -> Int {
        b == 0 ? a : gcd(b, a % b)
    }

    // MARK: - Period

    static func computeLoops(R: Double, r: Double) -> Int {
        let rInt = max(1, Int(r))
        let RInt = max(2, Int(R))
        let g = gcd(rInt, RInt)
        return g == 0 ? 1 : rInt / g
    }

    // MARK: - Point Generation

    /// Returns 6001 CGPoints (indices 0...6000) in raw math space (centered at origin).
    static func computePoints(R: Double, r: Double, d: Double) -> [CGPoint] {
        let rClamped = max(1, min(r, R - 1))
        let loops = computeLoops(R: R, r: rClamped)
        let steps = 6000

        var points = [CGPoint]()
        points.reserveCapacity(steps + 1)

        for i in 0...steps {
            let t = 2.0 * .pi * Double(loops) * Double(i) / Double(steps)
            let x = (R - rClamped) * cos(t) + d * cos((R - rClamped) * t / rClamped)
            let y = (R - rClamped) * sin(t) - d * sin((R - rClamped) * t / rClamped)
            points.append(CGPoint(x: x, y: y))
        }
        return points
    }

    // MARK: - Scale & Center

    /// Scales raw math-space points to fit within canvasSize, with a margin on each edge.
    static func scalePoints(_ points: [CGPoint], canvasSize: CGFloat, margin: CGFloat = 28) -> [CGPoint] {
        guard !points.isEmpty else { return [] }

        var maxExtent: CGFloat = 1
        for p in points {
            let e = max(abs(p.x), abs(p.y))
            if e > maxExtent { maxExtent = e }
        }

        let scale = (canvasSize / 2 - margin) / maxExtent
        let cx = canvasSize / 2
        let cy = canvasSize / 2

        return points.map { p in
            CGPoint(x: cx + p.x * scale, y: cy + p.y * scale)
        }
    }

    // MARK: - Ghost Trace (lower resolution for preview)

    static func computeGhostPoints(R: Double, r: Double, d: Double, steps: Int = 900) -> [CGPoint] {
        let rClamped = max(1, min(r, R - 1))
        let loops = computeLoops(R: R, r: rClamped)
        var points = [CGPoint]()
        points.reserveCapacity(steps + 1)
        for i in 0...steps {
            let t = 2.0 * .pi * Double(loops) * Double(i) / Double(steps)
            let x = (R - rClamped) * cos(t) + d * cos((R - rClamped) * t / rClamped)
            let y = (R - rClamped) * sin(t) - d * sin((R - rClamped) * t / rClamped)
            points.append(CGPoint(x: x, y: y))
        }
        return points
    }
}
