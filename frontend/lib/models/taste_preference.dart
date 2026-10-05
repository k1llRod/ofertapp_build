class TastePreferenceModel {
  final int? id;
  final int categoryId;
  final String categoryName;
  final String categoryIcon;
  final List<String> tags;
  final double maxDistanceKm;

  TastePreferenceModel({
    this.id,
    required this.categoryId,
    required this.categoryName,
    required this.categoryIcon,
    required this.tags,
    this.maxDistanceKm = 10.0,
  });

  factory TastePreferenceModel.fromJson(Map<String, dynamic> json) {
    return TastePreferenceModel(
      id: json['id'] as int?,
      categoryId: json['category_id'] as int,
      categoryName: json['category_name'] as String? ?? 'General',
      categoryIcon: json['category_icon'] as String? ?? '🏷️',
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      maxDistanceKm: (json['max_distance_km'] as num?)?.toDouble() ?? 10.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'category_id': categoryId,
      'tags': tags,
      'max_distance_km': maxDistanceKm,
    };
  }

  TastePreferenceModel copyWith({
    List<String>? tags,
    double? maxDistanceKm,
  }) {
    return TastePreferenceModel(
      id: id,
      categoryId: categoryId,
      categoryName: categoryName,
      categoryIcon: categoryIcon,
      tags: tags ?? this.tags,
      maxDistanceKm: maxDistanceKm ?? this.maxDistanceKm,
    );
  }
}
