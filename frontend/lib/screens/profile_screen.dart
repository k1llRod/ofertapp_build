import 'package:flutter/material.dart';
import '../models/user_profile.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isLoading = true;
  bool _isSaving = false;
  UserProfileModel? _profile;

  // Controladores de texto para perfil
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _bioController = TextEditingController();
  final _logoController = TextEditingController();
  final _bannerController = TextEditingController();

  // Controladores para Redes Sociales
  final _instagramController = TextEditingController();
  final _facebookController = TextEditingController();
  final _whatsappController = TextEditingController();
  final _twitterController = TextEditingController();
  final _websiteController = TextEditingController();

  // Controladores para Cambio de Contraseña
  final _currentPwdController = TextEditingController();
  final _newPwdController = TextEditingController();
  final _confirmPwdController = TextEditingController();
  bool _isChangingPassword = false;
  bool _hideCurrentPwd = true;
  bool _hideNewPwd = true;
  bool _hideConfirmPwd = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _bioController.dispose();
    _logoController.dispose();
    _bannerController.dispose();
    _instagramController.dispose();
    _facebookController.dispose();
    _whatsappController.dispose();
    _twitterController.dispose();
    _websiteController.dispose();
    _currentPwdController.dispose();
    _newPwdController.dispose();
    _confirmPwdController.dispose();
    super.dispose();
  }

  Future<void> _loadProfile() async {
    setState(() => _isLoading = true);
    final p = await ApiService.getUserProfile();
    setState(() {
      _profile = p;
      _nameController.text = p.fullName;
      _emailController.text = p.email;
      _phoneController.text = p.phone ?? '';
      _bioController.text = p.bio ?? '';
      _logoController.text = p.logoUrl ?? '';
      _bannerController.text = p.bannerUrl ?? '';
      _instagramController.text = p.socialInstagram ?? '';
      _facebookController.text = p.socialFacebook ?? '';
      _whatsappController.text = p.socialWhatsapp ?? '';
      _twitterController.text = p.socialTwitter ?? '';
      _websiteController.text = p.website ?? '';
      _isLoading = false;
    });
  }

  Future<void> _saveProfile() async {
    if (_nameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('El nombre no puede estar vacío')),
      );
      return;
    }

    setState(() => _isSaving = true);
    final updated = UserProfileModel(
      id: _profile?.id ?? 0,
      email: _emailController.text.trim(),
      fullName: _nameController.text.trim(),
      phone: _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
      role: _profile?.role ?? 'user',
      isActive: _profile?.isActive ?? true,
      logoUrl: _logoController.text.trim().isEmpty ? null : _logoController.text.trim(),
      bannerUrl: _bannerController.text.trim().isEmpty ? null : _bannerController.text.trim(),
      bio: _bioController.text.trim().isEmpty ? null : _bioController.text.trim(),
      socialInstagram: _instagramController.text.trim().isEmpty ? null : _instagramController.text.trim(),
      socialFacebook: _facebookController.text.trim().isEmpty ? null : _facebookController.text.trim(),
      socialTwitter: _twitterController.text.trim().isEmpty ? null : _twitterController.text.trim(),
      socialWhatsapp: _whatsappController.text.trim().isEmpty ? null : _whatsappController.text.trim(),
      website: _websiteController.text.trim().isEmpty ? null : _websiteController.text.trim(),
    );

    final res = await ApiService.updateUserProfile(updated);
    setState(() {
      if (res != null) _profile = res;
      _isSaving = false;
    });

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: Color(0xFF059669),
          content: Text('✓ ¡Perfil actualizado correctamente!'),
        ),
      );
    }
  }

  Future<void> _submitChangePassword() async {
    final current = _currentPwdController.text;
    final newPwd = _newPwdController.text;
    final confirm = _confirmPwdController.text;

    if (current.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ingresa tu contraseña actual')),
      );
      return;
    }
    if (newPwd.length < 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('La nueva contraseña debe tener al menos 6 caracteres')),
      );
      return;
    }
    if (newPwd != confirm) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Las contraseñas no coinciden')),
      );
      return;
    }

    setState(() => _isChangingPassword = true);
    final res = await ApiService.changePassword(
      currentPassword: current,
      newPassword: newPwd,
      confirmPassword: confirm,
    );
    setState(() => _isChangingPassword = false);

    if (mounted) {
      if (res['success'] == true) {
        _currentPwdController.clear();
        _newPwdController.clear();
        _confirmPwdController.clear();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFF059669),
            content: Text('✓ ${res['message']}'),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFFDC2626),
            content: Text('⚠️ ${res['message']}'),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: AppTheme.primary)),
      );
    }

    final bannerUrl = _bannerController.text.trim();
    final logoUrl = _logoController.text.trim();

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Mi Perfil y Cuenta',
          style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
        ),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadProfile,
            tooltip: 'Recargar perfil',
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // --- HEADER VISUAL INTERACTIVO CON BANNER Y LOGO ---
            Stack(
              clipBehavior: Clip.none,
              children: [
                // Banner
                Container(
                  height: 140,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFF59E0B), Color(0xFFD97706), Color(0xFFB45309)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    image: bannerUrl.isNotEmpty
                        ? DecorationImage(
                            image: NetworkImage(bannerUrl),
                            fit: BoxFit.cover,
                          )
                        : null,
                  ),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    alignment: Alignment.topRight,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text(
                        '🖼️ Portada',
                        style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ),

                // Logo Avatar Superpuesto
                Positioned(
                  bottom: -40,
                  left: 20,
                  child: Container(
                    width: 84,
                    height: 84,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 3.5),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.2),
                          blurRadius: 8,
                          offset: const Offset(0, 3),
                        )
                      ],
                      color: AppTheme.primary,
                      image: logoUrl.isNotEmpty
                          ? DecorationImage(
                              image: NetworkImage(logoUrl),
                              fit: BoxFit.cover,
                            )
                          : null,
                    ),
                    child: logoUrl.isEmpty
                        ? Center(
                            child: Text(
                              _nameController.text.isNotEmpty
                                  ? _nameController.text.substring(0, 1).toUpperCase()
                                  : '👤',
                              style: const TextStyle(
                                fontSize: 32,
                                fontWeight: FontWeight.w900,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                          )
                        : null,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 50),

            // Badge de Rol y Nombre
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _nameController.text.isNotEmpty ? _nameController.text : 'Mi Perfil',
                          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF0F172A)),
                        ),
                        Text(
                          _emailController.text,
                          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: _profile?.role == 'merchant' ? const Color(0xFFFEF3C7) : const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: _profile?.role == 'merchant' ? const Color(0xFFFCD34D) : const Color(0xFFA7F3D0),
                      ),
                    ),
                    child: Text(
                      _profile?.role == 'merchant'
                          ? '🏪 Comercio'
                          : (_profile?.role == 'admin' ? '🛡️ Admin' : '👤 Consumidor'),
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: _profile?.role == 'merchant' ? const Color(0xFFB45309) : const Color(0xFF065F46),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // FORMULARIO PRINCIPAL
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // --- SECCIÓN 1: DATOS BÁSICOS & CONTACTO ---
                  _buildSectionHeader('👤 Datos de Perfil y Contacto'),
                  const SizedBox(height: 8),

                  Card(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    elevation: 1,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          TextField(
                            controller: _nameController,
                            decoration: const InputDecoration(
                              labelText: 'Nombre Completo o Razón Social *',
                              prefixIcon: Icon(Icons.person_outline),
                              border: OutlineInputBorder(),
                            ),
                            onChanged: (_) => setState(() {}),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _emailController,
                            keyboardType: TextInputType.emailAddress,
                            decoration: const InputDecoration(
                              labelText: 'Correo Electrónico *',
                              prefixIcon: Icon(Icons.email_outlined),
                              border: OutlineInputBorder(),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _phoneController,
                            keyboardType: TextInputType.phone,
                            decoration: const InputDecoration(
                              labelText: 'Número de Contacto / Teléfono',
                              prefixIcon: Icon(Icons.phone_outlined),
                              border: OutlineInputBorder(),
                              hintText: '+54 9 11 1234-5678',
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _bioController,
                            maxLines: 2,
                            decoration: const InputDecoration(
                              labelText: 'Descripción / Biografía',
                              prefixIcon: Icon(Icons.notes_outlined),
                              border: OutlineInputBorder(),
                              hintText: 'Presenta tu negocio o intereses...',
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _logoController,
                            decoration: const InputDecoration(
                              labelText: 'URL del Logo o Avatar',
                              prefixIcon: Icon(Icons.image_outlined),
                              border: OutlineInputBorder(),
                              hintText: 'https://...',
                            ),
                            onChanged: (_) => setState(() {}),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _bannerController,
                            decoration: const InputDecoration(
                              labelText: 'URL del Banner de Portada',
                              prefixIcon: Icon(Icons.panorama_outlined),
                              border: OutlineInputBorder(),
                              hintText: 'https://...',
                            ),
                            onChanged: (_) => setState(() {}),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // --- SECCIÓN 2: REDES SOCIALES ---
                  _buildSectionHeader('🌐 Redes Sociales y Web'),
                  const SizedBox(height: 8),

                  Card(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    elevation: 1,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          TextField(
                            controller: _instagramController,
                            decoration: const InputDecoration(
                              labelText: 'Instagram',
                              prefixIcon: Icon(Icons.camera_alt_outlined, color: Color(0xFFE1306C)),
                              border: OutlineInputBorder(),
                              hintText: '@mi_usuario o enlace',
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _whatsappController,
                            keyboardType: TextInputType.phone,
                            decoration: const InputDecoration(
                              labelText: 'WhatsApp Directo',
                              prefixIcon: Icon(Icons.chat_bubble_outline, color: Color(0xFF25D366)),
                              border: OutlineInputBorder(),
                              hintText: '+5491122334455',
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _facebookController,
                            decoration: const InputDecoration(
                              labelText: 'Facebook',
                              prefixIcon: Icon(Icons.facebook_outlined, color: Color(0xFF1877F2)),
                              border: OutlineInputBorder(),
                              hintText: 'facebook.com/usuario',
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _twitterController,
                            decoration: const InputDecoration(
                              labelText: 'X (Twitter)',
                              prefixIcon: Icon(Icons.alternate_email, color: Color(0xFF0F172A)),
                              border: OutlineInputBorder(),
                              hintText: '@usuario',
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _websiteController,
                            keyboardType: TextInputType.url,
                            decoration: const InputDecoration(
                              labelText: 'Sitio Web / Tienda Online',
                              prefixIcon: Icon(Icons.language_outlined, color: Color(0xFF0284C7)),
                              border: OutlineInputBorder(),
                              hintText: 'https://mytienda.com',
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // BOTÓN GUARDAR PERFIL
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isSaving ? null : _saveProfile,
                      icon: _isSaving
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : const Icon(Icons.save_outlined),
                      label: Text(
                        _isSaving ? 'Guardando cambios...' : '💾 Guardar Datos y Redes del Perfil',
                        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                      ),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        backgroundColor: AppTheme.primary,
                        foregroundColor: const Color(0xFF0F172A),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // --- SECCIÓN 3: CAMBIO DE CONTRASEÑA ---
                  _buildSectionHeader('🔒 Seguridad y Cambio de Contraseña'),
                  const SizedBox(height: 8),

                  Card(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    elevation: 1,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const Text(
                            'Actualiza tu clave de acceso ingresando tu contraseña actual y la nueva contraseña:',
                            style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                          ),
                          const SizedBox(height: 14),
                          TextField(
                            controller: _currentPwdController,
                            obscureText: _hideCurrentPwd,
                            decoration: InputDecoration(
                              labelText: 'Contraseña Actual *',
                              prefixIcon: const Icon(Icons.lock_outline),
                              border: const OutlineInputBorder(),
                              suffixIcon: IconButton(
                                icon: Icon(_hideCurrentPwd ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                                onPressed: () => setState(() => _hideCurrentPwd = !_hideCurrentPwd),
                              ),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _newPwdController,
                            obscureText: _hideNewPwd,
                            decoration: InputDecoration(
                              labelText: 'Nueva Contraseña (mín 6 caracteres) *',
                              prefixIcon: const Icon(Icons.vpn_key_outlined),
                              border: const OutlineInputBorder(),
                              suffixIcon: IconButton(
                                icon: Icon(_hideNewPwd ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                                onPressed: () => setState(() => _hideNewPwd = !_hideNewPwd),
                              ),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _confirmPwdController,
                            obscureText: _hideConfirmPwd,
                            decoration: InputDecoration(
                              labelText: 'Confirmar Nueva Contraseña *',
                              prefixIcon: const Icon(Icons.check_circle_outline),
                              border: const OutlineInputBorder(),
                              suffixIcon: IconButton(
                                icon: Icon(_hideConfirmPwd ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                                onPressed: () => setState(() => _hideConfirmPwd = !_hideConfirmPwd),
                              ),
                            ),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            onPressed: _isChangingPassword ? null : _submitChangePassword,
                            icon: _isChangingPassword
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                  )
                                : const Icon(Icons.lock_reset),
                            label: Text(
                              _isChangingPassword ? 'Actualizando...' : '🔑 Actualizar Mi Contraseña',
                              style: const TextStyle(fontWeight: FontWeight.w800),
                            ),
                            style: ElevatedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              backgroundColor: const Color(0xFF0F172A),
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 30),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w900,
        color: Color(0xFF1E293B),
        letterSpacing: -0.3,
      ),
    );
  }
}
