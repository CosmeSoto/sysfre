import * as Yup from 'yup';

/**
 * Esquema de validación para formulario de login
 */
export const loginSchema = Yup.object().shape({
  email: Yup.string()
    .email('Ingrese un correo electrónico válido')
    .required('El correo electrónico es requerido'),
  password: Yup.string()
    .required('La contraseña es requerida')
});

/**
 * Esquema de validación para formulario de cliente
 */
export const clienteSchema = Yup.object().shape({
  tipo_identificacion: Yup.string()
    .required('El tipo de identificación es requerido'),
  identificacion: Yup.string()
    .required('La identificación es requerida')
    .min(5, 'La identificación debe tener al menos 5 caracteres'),
  nombres: Yup.string()
    .required('Los nombres son requeridos')
    .min(2, 'Los nombres deben tener al menos 2 caracteres'),
  apellidos: Yup.string()
    .required('Los apellidos son requeridos')
    .min(2, 'Los apellidos deben tener al menos 2 caracteres'),
  email: Yup.string()
    .email('Ingrese un correo electrónico válido')
    .required('El correo electrónico es requerido'),
  telefono: Yup.string()
    .required('El teléfono es requerido'),
  direccion: Yup.string()
    .required('La dirección es requerida'),
  ciudad: Yup.string()
    .required('La ciudad es requerida'),
  provincia: Yup.string()
    .required('La provincia es requerida')
});

/**
 * Esquema de validación para formulario de producto
 */
export const productoSchema = Yup.object().shape({
  codigo: Yup.string()
    .required('El código es requerido'),
  nombre: Yup.string()
    .required('El nombre es requerido')
    .min(3, 'El nombre debe tener al menos 3 caracteres'),
  descripcion: Yup.string(),
  precio_compra: Yup.number()
    .required('El precio de compra es requerido')
    .min(0, 'El precio de compra debe ser mayor o igual a 0'),
  precio_venta: Yup.number()
    .required('El precio de venta es requerido')
    .min(0, 'El precio de venta debe ser mayor o igual a 0')
    .test(
      'is-greater-than-purchase',
      'El precio de venta debe ser mayor que el precio de compra',
      function(value) {
        const { precio_compra } = this.parent;
        return !precio_compra || !value || value >= precio_compra;
      }
    ),
  stock: Yup.number()
    .required('El stock es requerido')
    .min(0, 'El stock debe ser mayor o igual a 0'),
  stock_minimo: Yup.number()
    .required('El stock mínimo es requerido')
    .min(0, 'El stock mínimo debe ser mayor o igual a 0'),
  categoria: Yup.number()
    .required('La categoría es requerida'),
  iva: Yup.number()
    .required('El IVA es requerido')
    .min(0, 'El IVA debe ser mayor o igual a 0')
});

/**
 * Esquema de validación para formulario de venta
 */
export const ventaSchema = Yup.object().shape({
  cliente_id: Yup.number()
    .required('El cliente es requerido'),
  tipo: Yup.string()
    .required('El tipo de documento es requerido'),
  items: Yup.array()
    .of(
      Yup.object().shape({
        producto_id: Yup.number()
          .required('El producto es requerido'),
        cantidad: Yup.number()
          .required('La cantidad es requerida')
          .positive('La cantidad debe ser positiva'),
        precio_unitario: Yup.number()
          .required('El precio es requerido')
          .positive('El precio debe ser positivo'),
        descuento: Yup.number()
          .min(0, 'El descuento no puede ser negativo')
      })
    )
    .min(1, 'Debe agregar al menos un producto')
});

/**
 * Esquema de validación para formulario de pago
 */
export const pagoSchema = Yup.object().shape({
  metodo: Yup.string()
    .required('El método de pago es requerido'),
  monto: Yup.number()
    .required('El monto es requerido')
    .positive('El monto debe ser positivo'),
  referencia: Yup.string()
    .when('metodo', {
      is: (metodo) => metodo !== 'efectivo',
      then: Yup.string().required('La referencia es requerida para este método de pago')
    })
});

/**
 * Valida un RUC ecuatoriano
 * @param {string} ruc - RUC a validar
 * @returns {boolean} true si el RUC es válido, false en caso contrario
 */
export const validarRUC = (ruc) => {
  if (!ruc || ruc.length !== 13) {
    return false;
  }
  
  // Validar que los últimos dígitos sean 001
  if (ruc.substring(10, 13) !== '001') {
    return false;
  }
  
  // Validar el tipo de RUC (persona natural, sociedad o público)
  const tipoRUC = parseInt(ruc.substring(2, 3));
  if (tipoRUC < 0 || tipoRUC > 9) {
    return false;
  }
  
  if (tipoRUC < 6) {
    // Persona natural
    return validarCedula(ruc.substring(0, 10));
  } else if (tipoRUC === 6) {
    // Sociedad pública
    return validarRUCPublico(ruc.substring(0, 9));
  } else if (tipoRUC === 9) {
    // Sociedad privada
    return validarRUCPrivado(ruc.substring(0, 9));
  }
  
  return false;
};

/**
 * Valida una cédula ecuatoriana
 * @param {string} cedula - Cédula a validar
 * @returns {boolean} true si la cédula es válida, false en caso contrario
 */
export const validarCedula = (cedula) => {
  if (!cedula || cedula.length !== 10) {
    return false;
  }
  
  // Validar provincia
  const provincia = parseInt(cedula.substring(0, 2));
  if (provincia < 1 || provincia > 24) {
    return false;
  }
  
  // Validar tercer dígito
  const tercerDigito = parseInt(cedula.substring(2, 3));
  if (tercerDigito < 0 || tercerDigito > 5) {
    return false;
  }
  
  // Algoritmo de validación
  let suma = 0;
  for (let i = 0; i < 9; i++) {
    let digito = parseInt(cedula.charAt(i));
    if (i % 2 === 0) {
      digito *= 2;
      if (digito > 9) {
        digito -= 9;
      }
    }
    suma += digito;
  }
  
  const digitoVerificador = (10 - (suma % 10)) % 10;
  return digitoVerificador === parseInt(cedula.charAt(9));
};

// Funciones auxiliares para validar RUC
const validarRUCPublico = (ruc) => {
  let suma = 0;
  const coeficientes = [3, 2, 7, 6, 5, 4, 3, 2];
  
  for (let i = 0; i < 8; i++) {
    suma += parseInt(ruc.charAt(i)) * coeficientes[i];
  }
  
  const digitoVerificador = 11 - (suma % 11);
  return digitoVerificador === parseInt(ruc.charAt(8));
};

const validarRUCPrivado = (ruc) => {
  let suma = 0;
  const coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2];
  
  for (let i = 0; i < 9; i++) {
    suma += parseInt(ruc.charAt(i)) * coeficientes[i];
  }
  
  const digitoVerificador = 11 - (suma % 11);
  if (digitoVerificador === 11) {
    return parseInt(ruc.charAt(9)) === 0;
  }
  
  return digitoVerificador === parseInt(ruc.charAt(9));
};