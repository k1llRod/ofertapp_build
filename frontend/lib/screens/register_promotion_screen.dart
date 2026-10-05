import 'package:flutter/material.dart';
import '../models/category.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class RegisterPromotionScreen extends StatefulWidget {
  final VoidCallback onPromotionCreated;

  const RegisterPromotionScreen({Key? key, required this.onPromotionCreated}) : super(key: key);

  @override
  State<RegisterPromotionScreen> createState() => _RegisterPromotionScreenState();
}

class _RegisterPromotionScreenState extends State<RegisterPromotionScreen> {
  final _formKey = GlobalKey<FormState>();
  
  final _titleController = TextEditingController();
  final _descController = TextEditingController();
  final _originalPriceController = TextEditingController();
  final _tagsController = TextEditingController(text: 'pizza, artesanal, 2x1');
  final _addressController = TextEditingController(text: 'Av. Corrientes 1450, Centro');
  
  double _discountPercent = 30.0;
  int _selectedCategoryId = 1;
  double _latitude = -34.6040;
  double _longitude = -58.3825;
  String _imageUrl = 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600';
  bool _isSubmitting = false;

  List<CategoryModel> _categories = [];

  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  Future<void> _loadCategories() async {
    final cats = await ApiService.getCategories();
    if (mounted) {
      setState(() {
        _categories = cats;
        if (cats.isNotEmpty) {
          _selectedCategoryId = cats.first.id;
        }
      });
    }
  }

  double get _calculatedPromoPrice {
    final orig = double.tryParse(_originalPriceController.text) ?? 0.0;
    return orig * (1.0 - (_discountPercent / 100.0));
  }

  Future<void> _submitPromotion() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    final tagsList = _tagsController.text
        .split(',')
        .map((t) => t.trim().toLowerCase())
        .where((t) => t.isNotEmpty)
        .toList();

    final payload = {
      'merchant_id': 1,
      'merchant_name': 'Pizzería Bella Napoli (Tu Comercio)',
      'title': _titleController.text.trim(),
      'description': _descController.text.trim(),
      'category_id': _selectedCategoryId,
      'original_price': double.parse(_originalPriceController.text),
      'discount_percent': _discountPercent,
      'image_url': _imageUrl,
      'tags': tagsList,
      'latitude': _latitude,
      'longitude': _longitude,
      'address': _addressController.text.trim(),
    };

    final success = await ApiService.registerPromotion(payload);

    setState(() => _isSubmitting = false);

    if (mounted) {
      if (success) {
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            title: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.green, size: 28),
                SizedBox(width: 8),
                Text('¡Promoción Publicada!'),
              ],
            ),
            content: const Text(
              'La promoción se guardó en el catálogo y se enviaron alertas automáticas a los usuarios con gustos afines y cercanos a tu ubicación.',
            ),
            actions: [
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  widget.onPromotionCreated();
                },
                child: const Text('Ver en Feed'),
              ),
            ],
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error al publicar la promoción. Revisa la conexión.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Registrar Promoción'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Banner informativo
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppTheme.primary.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.primary.withOpacity(0.2)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.campaign, color: AppTheme.primary, size: 28),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Al publicar una oferta, el sistema dispara alertas a usuarios cuyos gustos coincidan con la categoría y que estén cerca.',
                        style: TextStyle(fontSize: 13, height: 1.3),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Título
              const Text('Título de la Oferta *', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(
                  hintText: 'Ej: 2x1 en Pizzas de Masa Madre + Bebida',
                  prefixIcon: Icon(Icons.local_offer_outlined),
                ),
                validator: (val) => val == null || val.isEmpty ? 'El título es obligatorio' : null,
              ),
              const SizedBox(height: 16),

              // Descripción
              const Text('Descripción Detallada *', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              TextFormField(
                controller: _descController,
                maxLines: 3,
                decoration: const InputDecoration(
                  hintText: 'Describe qué incluye la oferta, condiciones y horarios de canje...',
                ),
                validator: (val) => val == null || val.isEmpty ? 'La descripción es obligatoria' : null,
              ),
              const SizedBox(height: 16),

              // Categoría
              const Text('Categoría *', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              DropdownButtonFormField<int>(
                value: _selectedCategoryId,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.category_outlined),
                ),
                items: _categories.map((c) {
                  return DropdownMenuItem<int>(
                    value: c.id,
                    child: Text('${c.icon}  ${c.name}'),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedCategoryId = val);
                },
              ),
              const SizedBox(height: 16),

              // Precios y Descuento
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Precio Normal (Bs.)', style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 6),
                        TextFormField(
                          controller: _originalPriceController,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(hintText: '100'),
                          onChanged: (_) => setState(() {}),
                          validator: (val) => val == null || double.tryParse(val) == null ? 'Ingresa un precio válido' : null,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Descuento: ${_discountPercent.toInt()}%', style: const TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 6),
                        Slider(
                          value: _discountPercent,
                          min: 5,
                          max: 90,
                          divisions: 17,
                          activeColor: AppTheme.primary,
                          label: '${_discountPercent.toInt()}%',
                          onChanged: (val) => setState(() => _discountPercent = val),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Precio Final Calculado
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Precio Promocional Final:', style: TextStyle(fontWeight: FontWeight.bold)),
                    Text(
                      'Bs. ${_calculatedPromoPrice.toStringAsFixed(0)}',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.green.shade800,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Etiquetas / Gustos a los que apunta
              const Text('Etiquetas de afinidad (tags para alertar usuarios)', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text(
                'Los usuarios que tengan estas palabras en sus gustos recibirán la alerta:',
                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
              ),
              const SizedBox(height: 6),
              TextFormField(
                controller: _tagsController,
                decoration: const InputDecoration(
                  hintText: 'pizza, artesanal, cena, 2x1, merienda',
                  prefixIcon: Icon(Icons.tag),
                ),
              ),
              const SizedBox(height: 16),

              // Ubicación del Comercio
              const Text('Ubicación del Local Comercial *', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              TextFormField(
                controller: _addressController,
                decoration: const InputDecoration(
                  hintText: 'Dirección física del local',
                  prefixIcon: Icon(Icons.place),
                ),
                validator: (val) => val == null || val.isEmpty ? 'La dirección es obligatoria' : null,
              ),
              const SizedBox(height: 8),

              // Presets de Geolocalización
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    ActionChip(
                      avatar: const Icon(Icons.my_location, size: 16, color: AppTheme.secondary),
                      label: const Text('Zona Centro (-34.6040, -58.3825)'),
                      onPressed: () {
                        setState(() {
                          _latitude = -34.6040;
                          _longitude = -58.3825;
                          _addressController.text = 'Av. Corrientes 1250, Centro';
                        });
                      },
                    ),
                    const SizedBox(width: 8),
                    ActionChip(
                      avatar: const Icon(Icons.location_city, size: 16, color: AppTheme.primary),
                      label: const Text('Recoleta / Norte (-34.5980, -58.3870)'),
                      onPressed: () {
                        setState(() {
                          _latitude = -34.5980;
                          _longitude = -58.3870;
                          _addressController.text = 'Av. Santa Fe 1420, Recoleta';
                        });
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Botón de Enviar
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: _isSubmitting ? null : _submitPromotion,
                  icon: _isSubmitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                        )
                      : const Icon(Icons.send_rounded),
                  label: Text(_isSubmitting ? 'Publicando y alertando...' : 'Publicar y Alertar Usuarios'),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
