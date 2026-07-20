import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('Login Apuradito')),
      body: Center(
        child: authProvider.isLoading
            ? const CircularProgressIndicator()
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton(
                    onPressed: () async {
                      await context.read<AuthProvider>().login(
                        'test@test.com',
                        'password',
                      );
                      if (context.mounted) {
                        context.go('/passenger');
                      }
                    },
                    child: const Text('Login as Passenger'),
                  ),
                  ElevatedButton(
                    onPressed: () async {
                      await context.read<AuthProvider>().login(
                        'driver@test.com',
                        'password',
                      );
                      if (context.mounted) {
                        context.go('/driver');
                      }
                    },
                    child: const Text('Login as Driver'),
                  ),
                  TextButton(
                    onPressed: () => context.push('/register'),
                    child: const Text('Register'),
                  ),
                ],
              ),
      ),
    );
  }
}
