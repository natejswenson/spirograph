import XCTest
@testable import SpirographStudio

final class SpiroMathTests: XCTestCase {

    // MARK: - GCD

    func testGCDBasic() {
        XCTAssertEqual(SpiroMath.gcd(150, 80), 10)
        XCTAssertEqual(SpiroMath.gcd(80, 150), 10)   // order-independent
        XCTAssertEqual(SpiroMath.gcd(7, 3), 1)
        XCTAssertEqual(SpiroMath.gcd(12, 8), 4)
    }

    func testGCDEdgeCases() {
        XCTAssertEqual(SpiroMath.gcd(5, 5), 5)
        XCTAssertEqual(SpiroMath.gcd(0, 5), 5)
        XCTAssertEqual(SpiroMath.gcd(5, 0), 5)
    }

    // MARK: - Loops

    func testLoops() {
        // loops = r / gcd(R, r) = 80 / gcd(150, 80) = 80 / 10 = 8
        XCTAssertEqual(SpiroMath.computeLoops(R: 150, r: 80), 8)
        XCTAssertEqual(SpiroMath.computeLoops(R: 100, r: 50), 1)
    }

    // MARK: - Point Generation

    func testPointCount() {
        let pts = SpiroMath.computePoints(R: 150, r: 80, d: 100)
        XCTAssertEqual(pts.count, 6001)
    }

    func testRClamping() {
        // r == R should be clamped to R-1 → no crash, no NaN
        let pts = SpiroMath.computePoints(R: 100, r: 100, d: 50)
        XCTAssertFalse(pts.isEmpty)
        for p in pts {
            XCTAssertFalse(p.x.isNaN, "x should not be NaN")
            XCTAssertFalse(p.y.isNaN, "y should not be NaN")
            XCTAssertFalse(p.x.isInfinite, "x should not be infinite")
            XCTAssertFalse(p.y.isInfinite, "y should not be infinite")
        }
    }

    func testRGreaterThanR_clamped() {
        // r > R should also be safe
        let pts = SpiroMath.computePoints(R: 80, r: 100, d: 50)
        XCTAssertFalse(pts.isEmpty)
        for p in pts {
            XCTAssertFalse(p.x.isNaN)
            XCTAssertFalse(p.y.isNaN)
        }
    }

    // MARK: - Scaling

    func testPointsAreCentered() {
        let pts = SpiroMath.computePoints(R: 150, r: 80, d: 100)
        let scaled = SpiroMath.scalePoints(pts, canvasSize: 390, margin: 28)
        XCTAssertEqual(scaled.count, pts.count)

        let xs = scaled.map { $0.x }
        let ys = scaled.map { $0.y }

        // All points should be within canvas bounds (with margin)
        XCTAssertTrue(xs.max()! <= 390 - 28 + 1, "Max x exceeds canvas with margin")
        XCTAssertTrue(xs.min()! >= 28 - 1,        "Min x exceeds canvas with margin")
        XCTAssertTrue(ys.max()! <= 390 - 28 + 1, "Max y exceeds canvas with margin")
        XCTAssertTrue(ys.min()! >= 28 - 1,        "Min y exceeds canvas with margin")
    }

    func testScaleEmptyPoints() {
        let result = SpiroMath.scalePoints([], canvasSize: 390, margin: 28)
        XCTAssertTrue(result.isEmpty)
    }
}
