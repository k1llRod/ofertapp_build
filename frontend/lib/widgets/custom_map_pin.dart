import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class CustomMapPin extends StatelessWidget {
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;
  final String? label;

  const CustomMapPin({
    Key? key,
    required this.icon,
    this.isSelected = false,
    required this.onTap,
    this.label,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedScale(
        scale: isSelected ? 1.18 : 1.0,
        duration: const Duration(milliseconds: 200),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (label != null && isSelected)
              Container(
                margin: const EdgeInsets.only(bottom: 4),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(8),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 4,
                    ),
                  ],
                ),
                child: Text(
                  label!,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            CustomPaint(
              size: const Size(38, 48),
              painter: _PinTeardropPainter(
                fillColor: isSelected ? const Color(0xFFD97706) : AppTheme.primary,
                strokeColor: Colors.white,
                hasShadow: true,
              ),
              child: SizedBox(
                width: 38,
                height: 48,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Center(
                    child: Icon(
                      icon,
                      color: Colors.white,
                      size: 19,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PinTeardropPainter extends CustomPainter {
  final Color fillColor;
  final Color strokeColor;
  final bool hasShadow;

  _PinTeardropPainter({
    required this.fillColor,
    required this.strokeColor,
    this.hasShadow = true,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final path = Path();
    final w = size.width;
    final h = size.height;

    // Pin shape with round top and pointed bottom
    final r = w / 2;
    path.moveTo(w / 2, h);
    path.cubicTo(w * 0.1, h * 0.65, 0, h * 0.45, 0, r);
    path.arcToPoint(
      Offset(w, r),
      radius: Radius.circular(r),
      clockwise: true,
    );
    path.cubicTo(w, h * 0.45, w * 0.9, h * 0.65, w / 2, h);
    path.close();

    if (hasShadow) {
      final shadowPaint = Paint()
        ..color = const Color(0xFFD97706).withOpacity(0.35)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 5);
      canvas.drawPath(path.shift(const Offset(0, 3)), shadowPaint);
    }

    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.fill;
    canvas.drawPath(path, fillPaint);

    final strokePaint = Paint()
      ..color = strokeColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.2;
    canvas.drawPath(path, strokePaint);
  }

  @override
  bool shouldRepaint(covariant _PinTeardropPainter oldDelegate) =>
      oldDelegate.fillColor != fillColor || oldDelegate.strokeColor != strokeColor;
}
