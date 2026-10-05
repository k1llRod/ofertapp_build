class UserProfileModel {
  final int id;
  final String email;
  final String fullName;
  final String? phone;
  final String role;
  final bool isActive;
  final String? logoUrl;
  final String? bannerUrl;
  final String? bio;
  final String? socialInstagram;
  final String? socialFacebook;
  final String? socialTwitter;
  final String? socialWhatsapp;
  final String? website;

  UserProfileModel({
    required this.id,
    required this.email,
    required this.fullName,
    this.phone,
    required this.role,
    this.isActive = true,
    this.logoUrl,
    this.bannerUrl,
    this.bio,
    this.socialInstagram,
    this.socialFacebook,
    this.socialTwitter,
    this.socialWhatsapp,
    this.website,
  });

  factory UserProfileModel.fromJson(Map<String, dynamic> json) {
    return UserProfileModel(
      id: json['id'] ?? 0,
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      phone: json['phone'],
      role: json['role'] ?? 'user',
      isActive: json['is_active'] ?? true,
      logoUrl: json['logo_url'],
      bannerUrl: json['banner_url'],
      bio: json['bio'],
      socialInstagram: json['social_instagram'],
      socialFacebook: json['social_facebook'],
      socialTwitter: json['social_twitter'],
      socialWhatsapp: json['social_whatsapp'],
      website: json['website'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'full_name': fullName,
      'email': email,
      'phone': phone,
      'logo_url': logoUrl,
      'banner_url': bannerUrl,
      'bio': bio,
      'social_instagram': socialInstagram,
      'social_facebook': socialFacebook,
      'social_twitter': socialTwitter,
      'social_whatsapp': socialWhatsapp,
      'website': website,
    };
  }

  UserProfileModel copyWith({
    int? id,
    String? email,
    String? fullName,
    String? phone,
    String? role,
    bool? isActive,
    String? logoUrl,
    String? bannerUrl,
    String? bio,
    String? socialInstagram,
    String? socialFacebook,
    String? socialTwitter,
    String? socialWhatsapp,
    String? website,
  }) {
    return UserProfileModel(
      id: id ?? this.id,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      phone: phone ?? this.phone,
      role: role ?? this.role,
      isActive: isActive ?? this.isActive,
      logoUrl: logoUrl ?? this.logoUrl,
      bannerUrl: bannerUrl ?? this.bannerUrl,
      bio: bio ?? this.bio,
      socialInstagram: socialInstagram ?? this.socialInstagram,
      socialFacebook: socialFacebook ?? this.socialFacebook,
      socialTwitter: socialTwitter ?? this.socialTwitter,
      socialWhatsapp: socialWhatsapp ?? this.socialWhatsapp,
      website: website ?? this.website,
    );
  }
}
