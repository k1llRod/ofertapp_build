import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/category.dart';
import '../models/promotion.dart';
import '../models/taste_preference.dart';
import '../models/notification_item.dart';
import '../models/user_profile.dart';

class ApiService {
  // Por defecto apunta al API Gateway en la IP local para pruebas en dispositivos móviles
  static String baseUrl = 'http://192.168.1.226:8000/api/v1';

  static int currentUserId = 2; // Juan Pérez (Usuario demo)
  static String? authToken;

  // --- CATEGORÍAS ---
  static Future<List<CategoryModel>> getCategories() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/categories')).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        return data.map((json) => CategoryModel.fromJson(json)).toList();
      }
    } catch (_) {}

    // Fallback de respaldo offline
    return [
      CategoryModel(id: 1, name: 'Gastronomía', slug: 'gastronomia', icon: '🍔'),
      CategoryModel(id: 2, name: 'Tecnología', slug: 'tecnologia', icon: '💻'),
      CategoryModel(id: 3, name: 'Moda y Calzado', slug: 'moda', icon: '👗'),
      CategoryModel(id: 4, name: 'Entretenimiento', slug: 'entretenimiento', icon: '🎟️'),
      CategoryModel(id: 5, name: 'Belleza y Spa', slug: 'belleza', icon: '💆'),
      CategoryModel(id: 6, name: 'Deportes y Fitness', slug: 'deportes', icon: '⚽'),
      CategoryModel(id: 7, name: 'Hogar y Muebles', slug: 'hogar', icon: '🛋️'),
      CategoryModel(id: 8, name: 'Servicios', slug: 'servicios', icon: '🛠️'),
    ];
  }

  // --- FEED DE PROMOCIONES (FILTRADO POR GUSTOS Y DISTANCIA GPS) ---
  static Future<List<PromotionModel>> getPromotionsFeed({
    double? lat,
    double? lon,
    int? categoryId,
    String? tasteTags,
    String? tasteCategories,
    double? maxDistanceKm,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (lat != null) queryParams['lat'] = lat.toString();
      if (lon != null) queryParams['lon'] = lon.toString();
      if (categoryId != null) queryParams['category_id'] = categoryId.toString();
      if (tasteTags != null && tasteTags.isNotEmpty) queryParams['taste_tags'] = tasteTags;
      if (tasteCategories != null && tasteCategories.isNotEmpty) queryParams['taste_categories'] = tasteCategories;
      if (maxDistanceKm != null) queryParams['max_distance_km'] = maxDistanceKm.toString();

      final uri = Uri.parse('$baseUrl/promotions/feed').replace(queryParameters: queryParams);
      final response = await http.get(uri).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        final List<dynamic> items = data['items'] as List<dynamic>;
        return items.map((json) => PromotionModel.fromJson(json)).toList();
      }
    } catch (_) {}

    // Datos de demostración enriquecidos con cercanía y gustos
    return [
      PromotionModel(
        id: 1,
        merchantId: 1,
        merchantName: 'Pizzería Bella Napoli',
        title: '2x1 en Pizzas Artesanales + Bebida',
        description: 'Disfruta de dos pizzas grandes al horno de leña a elección más una gaseosa de 1.5L.',
        categoryId: 1,
        categoryName: 'Gastronomía',
        categoryIcon: '🍔',
        originalPrice: 12000.0,
        discountPercent: 50.0,
        promoPrice: 6000.0,
        imageUrl: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600',
        tags: ['pizza', 'artesanal', '2x1', 'cena'],
        latitude: -34.6042,
        longitude: -58.3820,
        address: 'Av. Corrientes 1250, Centro',
        distanceKm: 0.35,
        distanceLabel: 'a 350 m',
        matchesTaste: true,
        viewsCount: 28,
      ),
      PromotionModel(
        id: 2,
        merchantId: 1,
        merchantName: 'TechZone Express',
        title: 'Auriculares Bluetooth Noise Cancelling',
        description: 'Auriculares inalámbricos con cancelación activa de ruido y 30hs de batería.',
        categoryId: 2,
        categoryName: 'Tecnología',
        categoryIcon: '💻',
        originalPrice: 45000.0,
        discountPercent: 35.0,
        promoPrice: 29250.0,
        imageUrl: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600',
        tags: ['auriculares', 'bluetooth', 'audio', 'gamer'],
        latitude: -34.6015,
        longitude: -58.3790,
        address: 'Florida 680, Galería Pacífico',
        distanceKm: 0.60,
        distanceLabel: 'a 600 m',
        matchesTaste: true,
        viewsCount: 42,
      ),
      PromotionModel(
        id: 3,
        merchantId: 1,
        merchantName: 'Café de Especialidad Origen',
        title: 'Combo Desayuno: Flat White + Croissant',
        description: 'Café de grano colombiano recién tostado más un croissant francés horneado al día.',
        categoryId: 1,
        categoryName: 'Gastronomía',
        categoryIcon: '🍔',
        originalPrice: 5500.0,
        discountPercent: 30.0,
        promoPrice: 3850.0,
        imageUrl: 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600',
        tags: ['cafe', 'desayuno', 'croissant', 'artesanal'],
        latitude: -34.6060,
        longitude: -58.3850,
        address: 'Lavalle 840, Centro',
        distanceKm: 0.85,
        distanceLabel: 'a 850 m',
        matchesTaste: true,
        viewsCount: 19,
      ),
      PromotionModel(
        id: 4,
        merchantId: 1,
        merchantName: 'Barber & Co Studio',
        title: 'Corte de Cabello + Perfilado de Barba',
        description: 'Servicio premium con toalla caliente, navaja tradicional y peinado.',
        categoryId: 5,
        categoryName: 'Belleza y Spa',
        categoryIcon: '💆',
        originalPrice: 14000.0,
        discountPercent: 25.0,
        promoPrice: 10500.0,
        imageUrl: 'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=600',
        tags: ['barberia', 'corte', 'barba'],
        latitude: -34.5980,
        longitude: -58.3870,
        address: 'Santa Fe 1420, Recoleta',
        distanceKm: 1.2,
        distanceLabel: 'a 1.2 km',
        matchesTaste: false,
        viewsCount: 15,
      ),
      PromotionModel(
        id: 5,
        merchantId: 1,
        merchantName: 'FitLife Gym & Training',
        title: 'Pase Libre Mensual con 40% OFF',
        description: 'Acceso total a sala de musculación, funcional y spinning.',
        categoryId: 6,
        categoryName: 'Deportes y Fitness',
        categoryIcon: '⚽',
        originalPrice: 35000.0,
        discountPercent: 40.0,
        promoPrice: 21000.0,
        imageUrl: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600',
        tags: ['gimnasio', 'fitness', 'musculacion'],
        latitude: -34.6100,
        longitude: -58.3750,
        address: 'Belgrano 920, San Telmo',
        distanceKm: 1.8,
        distanceLabel: 'a 1.8 km',
        matchesTaste: false,
        viewsCount: 31,
      ),
    ];
  }

  // --- REGISTRO DE PROMOCIÓN (COMERCIO) ---
  static Future<bool> registerPromotion(Map<String, dynamic> promoData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/promotions'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(promoData),
      ).timeout(const Duration(seconds: 5));

      return response.statusCode == 201 || response.statusCode == 200;
    } catch (_) {
      return true; // Éxito en modo local/demo
    }
  }

  // --- GUSTOS DEL USUARIO ---
  static Future<List<TastePreferenceModel>> getUserTastes() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/tastes/me'),
        headers: authToken != null ? {'Authorization': 'Bearer $authToken'} : {},
      ).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        return data.map((json) => TastePreferenceModel.fromJson(json)).toList();
      }
    } catch (_) {}

    // Gustos por defecto para el usuario demo Juan
    return [
      TastePreferenceModel(
        categoryId: 1,
        categoryName: 'Gastronomía',
        categoryIcon: '🍔',
        tags: ['pizza', 'artesanal', 'cafe', 'hamburguesas'],
        maxDistanceKm: 10.0,
      ),
      TastePreferenceModel(
        categoryId: 2,
        categoryName: 'Tecnología',
        categoryIcon: '💻',
        tags: ['auriculares', 'computacion', 'gamer', 'gadgets'],
        maxDistanceKm: 15.0,
      ),
    ];
  }

  static Future<bool> saveUserTastes(List<TastePreferenceModel> tastes) async {
    try {
      final body = {
        'preferences': tastes.map((t) => t.toJson()).toList(),
      };
      final response = await http.put(
        Uri.parse('$baseUrl/tastes/me'),
        headers: {
          'Content-Type': 'application/json',
          if (authToken != null) 'Authorization': 'Bearer $authToken',
        },
        body: jsonEncode(body),
      ).timeout(const Duration(seconds: 4));

      return response.statusCode == 200;
    } catch (_) {
      return true;
    }
  }

  // --- ALERTAS Y NOTIFICACIONES ---
  static Future<List<NotificationItemModel>> getNotifications() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/notifications/user/$currentUserId'),
      ).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        final List<dynamic> items = data['items'] as List<dynamic>;
        return items.map((json) => NotificationItemModel.fromJson(json)).toList();
      }
    } catch (_) {}

    // Alertas por defecto de muestra
    return [
      NotificationItemModel(
        id: 1,
        userId: currentUserId,
        promotionId: 1,
        title: '🍕 ¡Oferta de tu gusto: 50% OFF!',
        message: 'Pizzería Bella Napoli publicó "2x1 en Pizzas Artesanales + Bebida" a solo 350 m de tu ubicación.',
        categoryName: 'Gastronomía',
        distanceKm: 0.35,
        discountPercent: 50.0,
        isRead: false,
        createdAt: 'Hace 10 min',
      ),
      NotificationItemModel(
        id: 2,
        userId: currentUserId,
        promotionId: 2,
        title: '💻 ¡Alerta Tech: 35% OFF!',
        message: 'TechZone Express lanzó "Auriculares Bluetooth Noise Cancelling" cerca de tu zona comercial preferida.',
        categoryName: 'Tecnología',
        distanceKm: 0.60,
        discountPercent: 35.0,
        isRead: false,
        createdAt: 'Hace 45 min',
      ),
      NotificationItemModel(
        id: 3,
        userId: currentUserId,
        promotionId: 3,
        title: '☕ Desayuno con 30% OFF',
        message: 'Café de Especialidad Origen activó combo Flat White + Croissant a 850 m de distancia.',
        categoryName: 'Gastronomía',
        distanceKm: 0.85,
        discountPercent: 30.0,
        isRead: true,
        createdAt: 'Ayer',
      ),
    ];
  }

  static Future<bool> markNotificationAsRead(int notificationId) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/notifications/$notificationId/read'),
      ).timeout(const Duration(seconds: 3));
      return response.statusCode == 200;
    } catch (_) {
      return true;
    }
  }

  // --- PERFIL DE USUARIO Y SEGURIDAD ---
  static Future<UserProfileModel> getUserProfile() async {
    try {
      final headers = <String, String>{};
      if (authToken != null) headers['Authorization'] = 'Bearer $authToken';
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: headers,
      ).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        return UserProfileModel.fromJson(data);
      }
    } catch (_) {}

    // Fallback de demostración
    return UserProfileModel(
      id: currentUserId,
      email: 'usuario@ofertapp.com',
      fullName: 'Juan Pérez',
      phone: '+54 9 11 9988-7766',
      role: 'user',
      logoUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
      bannerUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200',
      bio: 'Amante de la gastronomía urbana, el café de especialidad y la tecnología móvil.',
      socialInstagram: '@juanperez_cba',
      socialWhatsapp: '+5491199887766',
      website: 'https://juanperez.me',
    );
  }

  static Future<UserProfileModel?> updateUserProfile(UserProfileModel profile) async {
    try {
      final headers = <String, String>{'Content-Type': 'application/json'};
      if (authToken != null) headers['Authorization'] = 'Bearer $authToken';
      final response = await http.put(
        Uri.parse('$baseUrl/auth/profile'),
        headers: headers,
        body: jsonEncode(profile.toJson()),
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        return UserProfileModel.fromJson(data);
      }
    } catch (_) {}
    return profile;
  }

  static Future<Map<String, dynamic>> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    try {
      final headers = <String, String>{'Content-Type': 'application/json'};
      if (authToken != null) headers['Authorization'] = 'Bearer $authToken';
      final response = await http.post(
        Uri.parse('$baseUrl/auth/change-password'),
        headers: headers,
        body: jsonEncode({
          'current_password': currentPassword,
          'new_password': newPassword,
          'confirm_password': confirmPassword,
        }),
      ).timeout(const Duration(seconds: 5));

      final Map<String, dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        return {'success': true, 'message': data['message'] ?? 'Contraseña actualizada correctamente'};
      } else {
        return {'success': false, 'message': data['detail'] ?? 'Error al actualizar contraseña'};
      }
    } catch (e) {
      return {'success': false, 'message': 'No se pudo conectar con el servidor'};
    }
  }
}
