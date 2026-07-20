import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class RegisterPage extends StatelessWidget {
  const RegisterPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Register Apuradito')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Registration Form Here'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => context.pop(),
              child: const Text('Back to Login'),
            ),
          ],
        ),
      ),
    );
  }
}
