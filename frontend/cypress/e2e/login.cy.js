// cypress/e2e/login.cy.js
describe('Login básico', () => {
  it('debería cargar la página de login', () => {
    cy.visit('/login');
    cy.contains('Iniciar sesión').should('exist');
  });
});