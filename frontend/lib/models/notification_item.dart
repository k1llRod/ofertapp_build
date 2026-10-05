class NotificationItemModel {
  final int id;
  final int userId;
  final int promotionId;
  final String title;
  final String message;
  final String? categoryName;
  final double? distanceKm;
  final double? discountPercent;
  bool isRead;
  final String createdAt;

  NotificationItemModel({
    required this.id,
    required this.userId,
    required this.promotionId,
    required this.title,
    required this.message,
    this.categoryName,
    this.distanceKm,
    this.discountPercent,
    this.isRead = false,
    required this.createdAt,
  });

  factory NotificationItemModel.fromJson(Map<String, dynamic> json) {
    return NotificationItemModel(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      promotionId: json['promotion_id'] as int,
      title: json['title'] as String,
      message: json['message'] as String,
      categoryName: json['category_name'] as String?,
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
      discountPercent: (json['discount_percent'] as num?)?.toDouble(),
      isRead: json['is_read'] as bool? ?? false,
      createdAt: json['created_at'] as String? ?? '',
    );
  }
}
