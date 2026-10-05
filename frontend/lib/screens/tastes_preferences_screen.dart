import 'package:flutter/material.dart';
import '../models/category.dart';
import '../models/taste_preference.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class TastesPreferencesScreen extends StatefulWidget {
  final VoidCallback onTastesUpdated;

  const TastesPreferencesScreen({Key? key, required this.onTastesUpdated}) : super(key: key);

  @override
  State<TastesPreferencesScreen> createState() => _TastesPreferencesScreenState();
}

class _TastesPreferencesScreenState extends State<TastesPreferencesScreen> {
  bool _isLoading = true;
  bool _isSaving = false;
  List<CategoryModel> _allCategories = [];
  Set<int> _selectedCategoryIds = {};
  
  final _tagsController = TextEditingController();
  double _notificationRadius = 12.0;

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    setState(() => _isLoading = true);
    final cats = await ApiService.getCategories();
    final userTastes = await ApiService.getUserTastes();

    final selectedIds = userTastes.map((t) => t.categoryId).toSet();
    final allTags = userTastes.expand((t) => t.tags).toSet().toList();
    if (userTastes.isNotEmpty) {
      _notificationRadius = userTastes.first.maxDistanceKm;
    }

    setState(() {
      _allCategories = cats;
      _selectedCategoryIds = selectedIds;
      _tagsController.text = allTags.join(', ');
      _isLoading = false;
    });
  }

  Future<void> _savePreferences() async {
    setState(() => _isSaving = true);

    final tags = _tagsController.text
        .split(',')
        .map((t) => t.trim().toLowerCase())
        .where((t) => t.isNotEmpty)
        .toList();

    final preferencesList = _selectedCategoryIds.map((catId) {
      final cat = _allCategories.firstWhere((c) => c.id == catId);
      return TastePreferenceModel(
        categoryId: cat.id,
        categoryName: cat.name,
        categoryIcon: cat.icon,
        tags: tags,
        maxDistanceKm: _notificationRadius,
      );
    }).toList();

    final success = await ApiService.saveUserTastes(preferencesList);

    setState(() => _isSaving = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? '¡Tus gustos fueron actualizados!' : 'Error al guardar'),
          backgroundColor: success ? AppTheme.secondary : Colors.red,
        ),
      );
      if (success) {
        widget.onTastesUpdated();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis Gustos y Preferencias'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Banner explicativo
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [AppTheme.primary, AppTheme.primaryDark],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Row(
                      children: [
                        Text('🎯', style: TextStyle(fontSize: 32)),
                        SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Personaliza tu experiencia',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                              SizedBox(height: 4),
                              Text(
                                'Filtrar ofertas y recibir alertas cuando comercios cercanos publiquen lo que te apasiona.',
                                style: TextStyle(color: Colors.white70, fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Selección de Categorías Favoritas
                  const Text(
                    '1. Selecciona tus Categorías Favoritas',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textDark),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Toca para activar o desactivar:',
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 12),

                  Wrap(
                    spacing: 10,
                    runSpacing: 10,
                    children: _allCategories.map((cat) {
                      final isSelected = _selectedCategoryIds.contains(cat.id);
                      return FilterChip(
                        avatar: Text(cat.icon, style: const TextStyle(fontSize: 16)),
                        label: Text(cat.name),
                        selected: isSelected,
                        selectedColor: AppTheme.primary.withOpacity(0.15),
                        checkmarkColor: AppTheme.primary,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                          side: BorderSide(
                            color: isSelected ? AppTheme.primary : Colors.grey.shade300,
                            width: isSelected ? 1.5 : 1,
                          ),
                        ),
                        labelStyle: TextStyle(
                          color: isSelected ? AppTheme.primary : AppTheme.textDark,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                        onSelected: (val) {
                          setState(() {
                            if (val) {
                              _selectedCategoryIds.add(cat.id);
                            } else {
                              _selectedCategoryIds.remove(cat.id);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),

                  // Palabras Clave / Tags
                  const Text(
                    '2. Palabras Clave de tu Interés',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textDark),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Escribe términos específicos separados por coma (ej: pizza, 2x1, sushi, gamer, zapatillas):',
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: _tagsController,
                    decoration: const InputDecoration(
                      hintText: 'pizza, artesanal, cafe, hamburguesas, apple',
                      prefixIcon: Icon(Icons.style_outlined),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Radio de Alertas
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        '3. Radio de Alertas Cercanas',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textDark),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.secondary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'Hasta ${_notificationRadius.toInt()} km',
                          style: const TextStyle(
                            color: AppTheme.secondary,
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Te notificaremos únicamente sobre ofertas dentro de esta distancia de tu ubicación GPS.',
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 8),
                  Slider(
                    value: _notificationRadius,
                    min: 1.0,
                    max: 30.0,
                    divisions: 29,
                    activeColor: AppTheme.secondary,
                    label: '${_notificationRadius.toInt()} km',
                    onChanged: (val) => setState(() => _notificationRadius = val),
                  ),
                  const SizedBox(height: 32),

                  // Botón Guardar
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton.icon(
                      onPressed: _isSaving ? null : _savePreferences,
                      icon: _isSaving
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                            )
                          : const Icon(Icons.save_rounded),
                      label: Text(_isSaving ? 'Guardando...' : 'Guardar mis Gustos'),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }
}
