import 'package:flutter/material.dart';
import 'home_feed_screen.dart';
import 'register_promotion_screen.dart';
import 'tastes_preferences_screen.dart';
import 'notifications_screen.dart';
import 'profile_screen.dart';
import '../theme/app_theme.dart';

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({Key? key}) : super(key: key);

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  void _navigateToTab(int index) {
    setState(() => _currentIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> screens = [
      HomeFeedScreen(onOpenPreferences: () => _navigateToTab(3)),
      RegisterPromotionScreen(onPromotionCreated: () => _navigateToTab(0)),
      const NotificationsScreen(),
      TastesPreferencesScreen(onTastesUpdated: () => _navigateToTab(0)),
      const ProfileScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: _navigateToTab,
        indicatorColor: AppTheme.primary.withOpacity(0.24),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.storefront_outlined),
            selectedIcon: Icon(Icons.storefront, color: Color(0xFF0F172A)),
            label: 'Ofertas',
          ),
          NavigationDestination(
            icon: Icon(Icons.add_circle_outline),
            selectedIcon: Icon(Icons.add_circle, color: Color(0xFF0F172A)),
            label: 'Publicar',
          ),
          NavigationDestination(
            icon: Icon(Icons.notifications_outlined),
            selectedIcon: Icon(Icons.notifications, color: Color(0xFF0F172A)),
            label: 'Alertas',
          ),
          NavigationDestination(
            icon: Icon(Icons.favorite_outline),
            selectedIcon: Icon(Icons.favorite, color: Color(0xFF0F172A)),
            label: 'Mis Gustos',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person, color: Color(0xFF0F172A)),
            label: 'Mi Perfil',
          ),
        ],
      ),
    );
  }
}
