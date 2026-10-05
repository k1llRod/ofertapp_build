import 'dart:async';
import 'package:flutter/material.dart';
import '../models/promotion.dart';
import '../theme/app_theme.dart';

class QrRedeemModal extends StatefulWidget {
  final PromotionModel promotion;
  final VoidCallback? onGoToMyCoupons;

  const QrRedeemModal({
    Key? key,
    required this.promotion,
    this.onGoToMyCoupons,
  }) : super(key: key);

  static Future<void> show(
    BuildContext context, {
    required PromotionModel promotion,
    VoidCallback? onGoToMyCoupons,
  }) {
    return showDialog(
      context: context,
      barrierColor: Colors.black.withOpacity(0.55),
      builder: (ctx) => QrRedeemModal(
        promotion: promotion,
        onGoToMyCoupons: onGoToMyCoupons,
      ),
    );
  }

  @override
  State<QrRedeemModal> createState() => _QrRedeemModalState();
}

class _QrRedeemModalState extends State<QrRedeemModal> {
  int _secondsLeft = 900; // 15 minutos exactos
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (mounted) {
        if (_secondsLeft > 0) {
          setState(() => _secondsLeft--);
        } else {
          t.cancel();
        }
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  String get _formattedTime {
    final m = (_secondsLeft ~/ 60).toString().padLeft(2, '0');
    final s = (_secondsLeft % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Tarjeta blanca principal
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 28),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(32),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.18),
                  blurRadius: 24,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Icono verde esmeralda con check
                Container(
                  width: 58,
                  height: 58,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppTheme.success,
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.success.withOpacity(0.35),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Icon(
                      Icons.check,
                      color: Colors.white,
                      size: 34,
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Título
                const Text(
                  'Canje Exitoso',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w900,
                    color: Color(0xFF0F172A),
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 4),

                // Subtítulo con temporizador
                Text(
                  'Válido por $_formattedTime',
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF94A3B8),
                  ),
                ),
                const SizedBox(height: 20),

                // Contenedor del código QR
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0), width: 1.5),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.04),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: CustomPaint(
                    size: const Size(160, 160),
                    painter: _VectorQrPainter(seed: widget.promotion.id),
                  ),
                ),
                const SizedBox(height: 18),

                // Estado activado
                const Text(
                  '¡Cupón Activado!',
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Válido por $_formattedTime',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF94A3B8),
                  ),
                ),
                const SizedBox(height: 22),

                // Botón CERRAR
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFF1F5F9),
                      foregroundColor: const Color(0xFF64748B),
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      textStyle: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.0,
                      ),
                    ),
                    child: const Text('CERRAR'),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Enlace inferior "Ver Mis Cupones"
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              if (widget.onGoToMyCoupons != null) {
                widget.onGoToMyCoupons!();
              }
            },
            style: TextButton.styleFrom(
              foregroundColor: Colors.white,
              textStyle: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                decoration: TextDecoration.underline,
              ),
            ),
            child: const Text('Ver Mis Cupones'),
          ),
        ],
      ),
    );
  }
}

/// Painter vectorial que renderiza un código QR limpio y nítido
class _VectorQrPainter extends CustomPainter {
  final int seed;

  _VectorQrPainter({required this.seed});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF0F172A)
      ..style = PaintingStyle.fill;

    final w = size.width;
    final h = size.height;
    final cellSize = w / 21; // Cuadrícula clásica de QR 21x21

    void drawFinderPattern(double x, double y) {
      // Borde exterior 7x7
      final outerRect = RRect.fromRectAndRadius(
        Rect.fromLTWH(x, y, cellSize * 7, cellSize * 7),
        const Radius.circular(5),
      );
      final borderPaint = Paint()
        ..color = const Color(0xFF0F172A)
        ..style = PaintingStyle.stroke
        ..strokeWidth = cellSize;
      canvas.drawRRect(outerRect.deflate(cellSize / 2), borderPaint);

      // Centro 3x3
      final centerRect = RRect.fromRectAndRadius(
        Rect.fromLTWH(x + cellSize * 2, y + cellSize * 2, cellSize * 3, cellSize * 3),
        const Radius.circular(3),
      );
      canvas.drawRRect(centerRect, paint);
    }

    // Dibujar 3 esquinas de anclaje
    drawFinderPattern(0, 0); // Superior Izquierda
    drawFinderPattern(w - cellSize * 7, 0); // Superior Derecha
    drawFinderPattern(0, h - cellSize * 7); // Inferior Izquierda

    // Patrón decorativo determinista basado en el seed de la promoción
    final pattern = [
      [8, 1, 3, 2], [12, 1, 2, 4], [8, 4, 4, 2], [14, 4, 3, 3],
      [1, 8, 3, 2], [5, 8, 2, 4], [9, 8, 4, 3], [14, 8, 2, 2], [17, 8, 3, 2],
      [8, 11, 2, 3], [11, 11, 4, 2], [16, 11, 2, 3],
      [8, 14, 3, 2], [12, 14, 2, 4], [15, 14, 3, 2],
      [8, 17, 4, 2], [13, 17, 2, 3], [16, 17, 4, 2],
      [9, 19, 3, 2], [13, 19, 4, 2], [18, 19, 3, 2],
    ];

    for (final p in pattern) {
      final px = p[0] * cellSize;
      final py = p[1] * cellSize;
      final pw = p[2] * cellSize;
      final ph = p[3] * cellSize;
      canvas.drawRRect(
        RRect.fromRectAndRadius(Rect.fromLTWH(px, py, pw, ph), const Radius.circular(2)),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _VectorQrPainter oldDelegate) => oldDelegate.seed != seed;
}
