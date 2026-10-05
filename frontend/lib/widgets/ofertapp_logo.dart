import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class OfertappLogo extends StatelessWidget {
  final double fontSize;
  final bool showIcon;

  const OfertappLogo({
    Key? key,
    this.fontSize = 22,
    this.showIcon = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (showIcon) ...[
          Container(
            width: fontSize * 1.3,
            height: fontSize * 1.3,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                colors: [Color(0xFF1E3A8A), Color(0xFF2563EB), Color(0xFFF59E0B)],
                begin: Alignment.bottomLeft,
                end: Alignment.topRight,
              ),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primary.withOpacity(0.3),
                  blurRadius: 6,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            padding: const EdgeInsets.all(2.2),
            child: Container(
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white,
              ),
              child: Center(
                child: Container(
                  width: fontSize * 0.65,
                  height: fontSize * 0.65,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    color: Color(0xFF1E3A8A),
                  ),
                  child: Center(
                    child: Container(
                      width: fontSize * 0.28,
                      height: fontSize * 0.28,
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        color: Color(0xFFF59E0B),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
        ],
        RichText(
          text: TextSpan(
            style: TextStyle(
              fontSize: fontSize,
              fontWeight: FontWeight.w900,
              letterSpacing: -0.5,
              fontFamily: 'sans-serif',
            ),
            children: const [
              TextSpan(
                text: 'Ofert',
                style: TextStyle(color: Color(0xFF0F172A)),
              ),
              TextSpan(
                text: 'App',
                style: TextStyle(color: Color(0xFFF59E0B)),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
