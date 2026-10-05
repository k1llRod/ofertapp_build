class PromotionModel {
  final int id;
  final int merchantId;
  final String merchantName;
  final String title;
  final String description;
  final int categoryId;
  final String categoryName;
  final String categoryIcon;
  final double originalPrice;
  final double discountPercent;
  final double promoPrice;
  final String? imageUrl;
  final List<String> tags;
  final double latitude;
  final double longitude;
  final String address;
  final double? distanceKm;
  final String? distanceLabel;
  final bool matchesTaste;
  final int viewsCount;

  PromotionModel({
    required this.id,
    required this.merchantId,
    required this.merchantName,
    required this.title,
    required this.description,
    required this.categoryId,
    required this.categoryName,
    required this.categoryIcon,
    required this.originalPrice,
    required this.discountPercent,
    required this.promoPrice,
    this.imageUrl,
    required this.tags,
    required this.latitude,
    required this.longitude,
    required this.address,
    this.distanceKm,
    this.distanceLabel,
    this.matchesTaste = false,
    this.viewsCount = 0,
  });

  factory PromotionModel.fromJson(Map<String, dynamic> json) {
    return PromotionModel(
      id: json['id'] as int,
      merchantId: json['merchant_id'] as int? ?? 1,
      merchantName: json['merchant_name'] as String? ?? 'Comercio',
      title: json['title'] as String,
      description: json['description'] as String? ?? '',
      categoryId: json['category_id'] as int? ?? 1,
      categoryName: json['category_name'] as String? ?? 'General',
      categoryIcon: json['category_icon'] as String? ?? '🏷️',
      originalPrice: (json['original_price'] as num).toDouble(),
      discountPercent: (json['discount_percent'] as num).toDouble(),
      promoPrice: (json['promo_price'] as num).toDouble(),
      imageUrl: json['image_url'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      address: json['address'] as String? ?? '',
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
      distanceLabel: json['distance_label'] as String?,
      matchesTaste: json['matches_taste'] as bool? ?? false,
      viewsCount: json['views_count'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'merchant_id': merchantId,
      'merchant_name': merchantName,
      'title': title,
      'description': description,
      'category_id': categoryId,
      'category_name': categoryName,
      'category_icon': categoryIcon,
      'original_price': originalPrice,
      'discount_percent': discountPercent,
      'promo_price': promoPrice,
      'image_url': imageUrl,
      'tags': tags,
      'latitude': latitude,
      'longitude': longitude,
      'address': address,
      'distance_km': distanceKm,
      'distance_label': distanceLabel,
      'matches_taste': matchesTaste,
      'views_count': viewsCount,
    };
  }
}
