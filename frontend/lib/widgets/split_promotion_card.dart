import 'package:flutter/material.dart';
import '../models/promotion.dart';
import '../theme/app_theme.dart';

class SplitPromotionCard extends StatelessWidget {
  final PromotionModel promotion;
  final VoidCallback onTap;
  final double width;

  const SplitPromotionCard({
    Key? key,
    required this.promotion,
    required this.onTap,
    this.width = 275,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: 145,
      margin: const EdgeInsets.only(right: 14, bottom: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.12),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(
          color: promotion.matchesTaste
              ? AppTheme.primary.withOpacity(0.6)
              : Colors.white.withOpacity(0.1),
          width: 1.5,
        ),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            child: Row(
              children: [
                // Columna Izquierda: Bloque Azul Noche con Datos y Botón
                Expanded(
                  flex: 62,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Color(0xFF1E3A8A), Color(0xFF0F172A)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // Nombre del Comercio
                        Text(
                          promotion.merchantName,
                          style: const TextStyle(
                            color: Color(0xFF93C5FD),
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),

                        // Titular de Descuento
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '-${promotion.discountPercent.toInt()}% Dto.',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.w900,
                                height: 1.1,
                                letterSpacing: -0.3,
                              ),
                            ),
                            Text(
                              promotion.title,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                height: 1.1,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),

                        // Distancia y Tiempo
                        Row(
                          children: [
                            const Icon(
                              Icons.location_on,
                              color: AppTheme.primary,
                              size: 11,
                            ),
                            const SizedBox(width: 2),
                            Text(
                              promotion.distanceLabel ?? '150m',
                              style: const TextStyle(
                                color: Color(0xFFCBD5E1),
                                fontSize: 10,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            const SizedBox(width: 6),
                            const Text('•', style: TextStyle(color: Color(0xFF64748B), fontSize: 10)),
                            const SizedBox(width: 6),
                            const Icon(
                              Icons.access_time,
                              color: Color(0xFF94A3B8),
                              size: 11,
                            ),
                            const SizedBox(width: 2),
                            const Expanded(
                              child: Text(
                                'Válido 1h',
                                style: TextStyle(
                                  color: Color(0xFFCBD5E1),
                                  fontSize: 10,
                                  fontWeight: FontWeight.w500,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),

                        // Botón naranja VER OFERTA
                        SizedBox(
                          width: double.infinity,
                          height: 28,
                          child: ElevatedButton(
                            onPressed: onTap,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppTheme.primary,
                              foregroundColor: const Color(0xFF0F172A),
                              elevation: 0,
                              padding: EdgeInsets.zero,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                            ),
                            child: const Text(
                              'VER OFERTA',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w900,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Columna Derecha: Imagen del Comercio / Producto
                Expanded(
                  flex: 38,
                  child: Container(
                    height: double.infinity,
                    color: const Color(0xFF1E293B),
                    child: Stack(
                      fit: StackFit.expand,
                      children: [
                        if (promotion.imageUrl != null && promotion.imageUrl!.isNotEmpty)
                          Image.network(
                            promotion.imageUrl!,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) => _buildPlaceholder(),
                          )
                        else
                          _buildPlaceholder(),
                        // Acento de Gusto
                        if (promotion.matchesTaste)
                          Positioned(
                            top: 6,
                            right: 6,
                            child: Container(
                              padding: const EdgeInsets.all(4),
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle,
                                color: AppTheme.primary,
                              ),
                              child: const Icon(
                                Icons.auto_awesome,
                                size: 10,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.grey.shade800, Colors.grey.shade900],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Center(
        child: Text(
          promotion.categoryIcon,
          style: const TextStyle(fontSize: 36),
        ),
      ),
    );
  }
}
