import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:apuradito_mobile/presentation/widgets/apuradito_button.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nombreController = TextEditingController();
  final _apellidoController = TextEditingController();
  final _emailController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _ciController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  
  String _selectedRol = 'pasajero';

  @override
  void dispose() {
    _nombreController.dispose();
    _apellidoController.dispose();
    _emailController.dispose();
    _telefonoController.dispose();
    _ciController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _register() async {
    if (_formKey.currentState!.validate()) {
      final authProvider = context.read<AuthProvider>();
      final success = await authProvider.register(
        email: _emailController.text,
        password: _passwordController.text,
        nombre: _nombreController.text,
        apellido: _apellidoController.text,
        ci: _ciController.text,
        telefono: _telefonoController.text,
        rol: _selectedRol,
      );

      if (!mounted) return;

      if (success) {
        if (_selectedRol == 'conductor') {
          context.go('/driver');
        } else {
          context.go('/passenger');
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Error al registrarse'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Widget _buildRoleCard(String rol, IconData icon, String label) {
    final isSelected = _selectedRol == rol;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() {
            _selectedRol = rol;
          });
        },
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF7C3AED).withOpacity(0.2) : const Color(0xFF1A1035),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? const Color(0xFF7C3AED) : Colors.transparent,
              width: 2,
            ),
          ),
          child: Column(
            children: [
              Icon(icon, color: isSelected ? const Color(0xFF7C3AED) : Colors.white54, size: 32),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  color: isSelected ? Colors.white : Colors.white54,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = context.watch<AuthProvider>().isLoading;

    return Scaffold(
      backgroundColor: const Color(0xFF0F0A1E),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Crear Cuenta',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 24),
                Row(
                  children: [
                    _buildRoleCard('pasajero', Icons.person, 'Pasajero'),
                    const SizedBox(width: 16),
                    _buildRoleCard('conductor', Icons.drive_eta, 'Conductor'),
                  ],
                ),
                const SizedBox(height: 24),
                _buildTextField(_nombreController, 'Nombre', Icons.person),
                const SizedBox(height: 16),
                _buildTextField(_apellidoController, 'Apellido', Icons.person_outline),
                const SizedBox(height: 16),
                _buildTextField(_emailController, 'Email', Icons.email, keyboardType: TextInputType.emailAddress),
                const SizedBox(height: 16),
                _buildTextField(_telefonoController, 'Teléfono', Icons.phone, keyboardType: TextInputType.phone),
                const SizedBox(height: 16),
                _buildTextField(_ciController, 'CI/Carnet', Icons.badge),
                const SizedBox(height: 16),
                _buildTextField(_passwordController, 'Contraseña', Icons.lock, obscureText: true),
                const SizedBox(height: 16),
                _buildTextField(_confirmPasswordController, 'Confirmar Contraseña', Icons.lock_outline, obscureText: true, validator: (v) {
                  if (v != _passwordController.text) return 'Las contraseñas no coinciden';
                  return null;
                }),
                const SizedBox(height: 32),
                ApuraditoButton(
                  text: 'Crear Cuenta',
                  isLoading: isLoading,
                  onPressed: _register,
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(TextEditingController controller, String hint, IconData icon, {bool obscureText = false, TextInputType? keyboardType, String? Function(String?)? validator}) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        filled: true,
        fillColor: const Color(0xFF1A1035),
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white54),
        prefixIcon: Icon(icon, color: Colors.white54),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF7C3AED)),
        ),
      ),
      validator: validator ?? (value) {
        if (value == null || value.isEmpty) {
          return 'Campo requerido';
        }
        return null;
      },
    );
  }
}
