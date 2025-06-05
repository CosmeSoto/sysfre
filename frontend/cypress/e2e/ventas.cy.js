// cypress/e2e/ventas.cy.js
describe('Ventas básico', () => {
  it('debería cargar la página', () => {
    cy.visit('/');
    cy.contains('SysFree').should('exist');
  });
});