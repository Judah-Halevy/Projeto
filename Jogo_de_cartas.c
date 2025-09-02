#include <stdio.h>

// Definindo estrutura para representar uma carta de cidade
struct CartaCidade {
    char estado[50];
    int codigo;
    char nome[100];
    int populacao;
    float pib;
    float area;
    int pontosTuristicos;
    float densidadePopulacional;
    float pibPerCapita;
};

// Função para registrar os dados de uma cidade
void registrarCarta(struct CartaCidade *carta) {
    printf("Estado: ");
    scanf(" %[^\n]", carta->estado);

    printf("Código da cidade: ");
    scanf("%d", &carta->codigo);

    printf("Nome da cidade: ");
    scanf(" %[^\n]", carta->nome);

    printf("População: ");
    scanf("%d", &carta->populacao);

    printf("PIB (em milhões): ");
    scanf("%f", &carta->pib);

    printf("Área (km²): ");
    scanf("%f", &carta->area);

    printf("Número de pontos turísticos: ");
    scanf("%d", &carta->pontosTuristicos);

    // Cálculos
    carta->densidadePopulacional = carta->populacao / carta->area;
    carta->pibPerCapita = (carta->pib * 1000000) / carta->populacao; // Convertendo PIB para unidade por habitante
}

// Função para exibir os dados da carta
void exibirCarta(struct CartaCidade carta) {
    printf("\n--- Dados da Cidade ---\n");
    printf("Estado: %s\n", carta.estado);
    printf("Código: %d\n", carta.codigo);
    printf("Nome: %s\n", carta.nome);
    printf("População: %d\n", carta.populacao);
    printf("PIB: R$ %.2f milhões\n", carta.pib);
    printf("Área: %.2f km²\n", carta.area);
    printf("Pontos turísticos: %d\n", carta.pontosTuristicos);
    printf("Densidade Populacional: %.2f hab/km²\n", carta.densidadePopulacional);
    printf("PIB per capita: R$ %.2f\n", carta.pibPerCapita);
}

int main() {
    int n, i;

    printf("Quantas cartas de cidades deseja registrar? ");
    scanf("%d", &n);

    struct CartaCidade cartas[n];

    for (i = 0; i < n; i++) {
        printf("\n--- Registrando carta %d ---\n", i + 1);
        registrarCarta(&cartas[i]);
    }

    for (i = 0; i < n; i++) {
        exibirCarta(cartas[i]);
    }

    return 0;
}
