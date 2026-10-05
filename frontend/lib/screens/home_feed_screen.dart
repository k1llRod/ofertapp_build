import 'package:flutter/material.dart';
import '../models/category.dart';
import '../models/promotion.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/location_header.dart';
import '../widgets/promotion_card.dart';

class HomeFeedScreen extends StatefulWidget {
  final VoidCallback onOpenPreferences;

  const HomeFeedScreen({Key? key, required this.onOpenPreferences}) : super(key: key);

  @override
  State<HomeFeedScreen> createState() => _HomeFeedScreenState();
}

class _HomeFeedScreenState extends State<HomeFeedScreen> {
  bool _isLoading = true;
  List<PromotionModel> _promotions = [];
  List<CategoryModel> _categories = [];
  
  int? _selectedCategoryId;
  bool _onlyMyTastes = true;
  double _userLat = -34.6037;
  double _userLon = -58.3816;
  String _locationName = 'Av. 9 de Julio y Corrientes, Centro';
  double _maxDistanceKm = 10.0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final cats = await ApiService.getCategories();
    final userTastes = await ApiService.getUserTastes();

    String? tasteCatsStr;
    String? tasteTagsStr;

    if (_onlyMyTastes && userTastes.isNotEmpty) {
      tasteCatsStr = userTastes.map((t) => t.categoryId).join(',');
      final allTags = userTastes.expand((t) => t.tags).toList();
      tasteTagsStr = allTags.join(',');
    }

    final promos = await ApiService.getPromotionsFeed(
      lat: _userLat,
      lon: _userLon,
      categoryId: _selectedCategoryId,
      tasteCategories: tasteCatsStr,
      tasteTags: tasteTagsStr,
      maxDistanceKm: _maxDistanceKm,
    );

    setState(() {
      _categories = cats;
      _promotions = promos;
      _isLoading = false;
    });
  }

  void _showRadiusDialog() {
    double tempRadius = _maxDistanceKm;
    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: const Row(
            children: [
              Icon(Icons.tune, color: AppTheme.primary),
              SizedBox(width: 8),
              Text(
                'Radio de Búsqueda',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Mostrar ofertas a un máximo de ${tempRadius.toStringAsFixed(0)} km desde tu ubicación actual:',
                style: const TextStyle(fontSize: 14),
              ),
              const SizedBox(height: 16),
              Slider(
                value: tempRadius,
                min: 1.0,
                max: 30.0,
                divisions: 29,
                activeColor: AppTheme.primary,
                label: '${tempRadius.toInt()} km',
                onChanged: (val) {
                  setDialogState(() => tempRadius = val);
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(ctx);
                setState(() => _maxDistanceKm = tempRadius);
                _loadData();
              },
              child: const Text('Aplicar'),
            ),
          ],
        ),
      ),
    );
  }

  void _showPromotionDetail(PromotionModel promo) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.primary,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '-${promo.discountPercent.toInt()}% OFF',
                    style: const TextStyle(color: Color(0xFF0F172A), fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.secondary.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    promo.distanceLabel ?? 'Cercano',
                    style: const TextStyle(color: AppTheme.secondary, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              promo.title,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              'Publicado por ${promo.merchantName}',
              style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 12),
            Text(
              promo.description,
              style: const TextStyle(fontSize: 15, height: 1.4),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Icon(Icons.location_on, color: AppTheme.secondary, size: 18),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    promo.address,
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 6,
              children: promo.tags
                  .map((t) => Chip(
                        label: Text('#$t', style: const TextStyle(fontSize: 12)),
                        padding: EdgeInsets.zero,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ))
                  .toList(),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Precio Normal: Bs. ${promo.originalPrice.toStringAsFixed(0)}',
                      style: TextStyle(
                        fontSize: 13,
                        decoration: TextDecoration.lineThrough,
                        color: Colors.grey.shade500,
                      ),
                    ),
                    Text(
                      'Bs. ${promo.promoPrice.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 26,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryDark,
                      ),
                    ),
                  ],
                ),
                ElevatedButton.icon(
                  onPressed: () {
                    Navigator.pop(ctx);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('¡Cupón activado para ${promo.merchantName}! Presenta en el local.'),
                        backgroundColor: AppTheme.secondary,
                      ),
                    );
                  },
                  icon: const Icon(Icons.local_offer),
                  label: const Text('Aprovechar Oferta'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppTheme.primary,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text('🏷️', style: TextStyle(fontSize: 18)),
            ),
            const SizedBox(width: 10),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Ofertapp',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                Text(
                  'Ofertas cerca de ti',
                  style: TextStyle(fontSize: 11, color: AppTheme.textLight),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Configurar Gustos',
            icon: const Icon(Icons.favorite, color: AppTheme.primary),
            onPressed: widget.onOpenPreferences,
          ),
        ],
      ),
      body: Column(
        children: [
          // Encabezado de Geolocalización GPS
          LocationHeader(
            locationText: _locationName,
            onChangeLocation: _showRadiusDialog,
          ),

          // Selector de Filtros Rápidos (Gustos & Categorías)
          Container(
            height: 50,
            color: Colors.white,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              children: [
                // Toggle de "Mis Gustos"
                FilterChip(
                  avatar: Icon(
                    Icons.auto_awesome,
                    size: 16,
                    color: _onlyMyTastes ? const Color(0xFF0F172A) : AppTheme.primary,
                  ),
                  label: const Text('Para mis gustos'),
                  selected: _onlyMyTastes,
                  selectedColor: AppTheme.primary,
                  checkmarkColor: const Color(0xFF0F172A),
                  labelStyle: TextStyle(
                    color: _onlyMyTastes ? const Color(0xFF0F172A) : AppTheme.textDark,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                  onSelected: (val) {
                    setState(() => _onlyMyTastes = val);
                    _loadData();
                  },
                ),
                const SizedBox(width: 8),
                // Todas
                FilterChip(
                  label: const Text('Todas'),
                  selected: _selectedCategoryId == null && !_onlyMyTastes,
                  selectedColor: AppTheme.secondary,
                  checkmarkColor: Colors.white,
                  labelStyle: TextStyle(
                    color: (_selectedCategoryId == null && !_onlyMyTastes) ? Colors.white : AppTheme.textDark,
                    fontSize: 12,
                  ),
                  onSelected: (val) {
                    setState(() {
                      _selectedCategoryId = null;
                      _onlyMyTastes = false;
                    });
                    _loadData();
                  },
                ),
                const SizedBox(width: 8),
                // Categorías
                ..._categories.map((cat) {
                  final isSelected = _selectedCategoryId == cat.id;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: FilterChip(
                      avatar: Text(cat.icon, style: const TextStyle(fontSize: 13)),
                      label: Text(cat.name),
                      selected: isSelected,
                      selectedColor: AppTheme.primary,
                      checkmarkColor: const Color(0xFF0F172A),
                      labelStyle: TextStyle(
                        color: isSelected ? const Color(0xFF0F172A) : AppTheme.textDark,
                        fontSize: 12,
                      ),
                      onSelected: (val) {
                        setState(() {
                          _selectedCategoryId = val ? cat.id : null;
                          if (val) _onlyMyTastes = false;
                        });
                        _loadData();
                      },
                    ),
                  );
                }),
              ],
            ),
          ),

          // Feed de Promociones
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
                : _promotions.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text('🔍', style: TextStyle(fontSize: 48)),
                            const SizedBox(height: 12),
                            const Text(
                              'No encontramos ofertas en este radio',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 8),
                            ElevatedButton(
                              onPressed: _showRadiusDialog,
                              child: const Text('Ampliar radio de búsqueda'),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        color: AppTheme.primary,
                        onRefresh: _loadData,
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          itemCount: _promotions.length,
                          itemBuilder: (context, index) {
                            final promo = _promotions[index];
                            return PromotionCard(
                              promotion: promo,
                              onTap: () => _showPromotionDetail(promo),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
}
