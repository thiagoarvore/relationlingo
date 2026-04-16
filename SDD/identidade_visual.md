# Identidade Visual - RelationLingo

## 1) Direção da marca

O app deve transmitir uma sensação de aprendizado leve, claro e confiável.
A estética é `clean`, com foco em legibilidade, simplicidade e consistência.
O produto é voltado para uso no Brasil, com linguagem e contexto locais.

## 2) Princípios visuais

- Clareza acima de decoração: a interface deve ser fácil de escanear.
- Consistência entre telas: componentes com aparência e comportamento previsíveis.
- Hierarquia bem definida: títulos, textos, botões e feedbacks devem ser facilmente distinguíveis.
- Acessibilidade como padrão: contraste adequado, foco visível e navegação intuitiva.

## 3) Stack e abordagem

- Base de UI: `Bootstrap 5` para estrutura, grid e componentes.
- Interações: usar `htmx` sempre que possível para evitar recarga completa de página.
- Personalização: aplicar tema próprio via variáveis CSS e utilitários, evitando aparência "padrão de template".

## 4) Paleta de cores

### Cores principais

- `Primary`: `#1D4ED8` (ações primárias, links principais)
- `Secondary`: `#0EA5A4` (destaques de apoio e badges informativos)
- `Accent`: `#F59E0B` (chamadas pontuais e estado de atenção)

### Neutros

- `Background`: `#F8FAFC`
- `Surface`: `#FFFFFF`
- `Text`: `#0F172A`
- `Text Muted`: `#64748B`
- `Border`: `#E2E8F0`

### Feedback

- `Success`: `#16A34A`
- `Warning`: `#D97706`
- `Danger`: `#DC2626`
- `Info`: `#2563EB`

## 5) Tipografia

- Fonte base: `"Nunito Sans", "Segoe UI", sans-serif`
- Fonte de títulos: `"Poppins", "Nunito Sans", sans-serif`
- Tamanho base: `16px`
- Altura de linha:
  - Corpo: `1.5`
  - Títulos: `1.2` a `1.3`

### Escala recomendada

- `H1`: 2rem / 700
- `H2`: 1.5rem / 700
- `H3`: 1.25rem / 600
- Corpo: 1rem / 400
- Legendas: 0.875rem / 400

## 6) Espaçamento e layout

- Usar escala de espaçamento em múltiplos de `4px` (`4, 8, 12, 16, 24, 32`).
- Container principal com respiro horizontal consistente (`px-3 px-md-4 px-lg-5`).
- Evitar blocos muito densos: priorizar `white space`.
- Grid Bootstrap deve ser o padrão para responsividade.

## 7) Componentes

### Cards

- Fundo branco (`Surface`)
- Borda suave (`1px solid #E2E8F0`)
- Canto arredondado (`12px` a `16px`)
- Sombra leve e discreta
- Padding interno confortável (`16px` a `24px`)

### Botões

- Mesmo padrão visual em todo o app (cor, raio, altura e peso de fonte).
- Botão primário:
  - Fundo `Primary`
  - Texto branco
  - Hover mais escuro em ~8%
- Botão secundário:
  - Fundo claro
  - Borda `Border`
  - Texto `Text`
- Altura mínima recomendada: `40px`
- `border-radius`: `10px`

### Inputs e formulários

- Inputs com fundo branco e borda `Border`.
- Foco com outline visível em `Primary` (não remover foco padrão sem substituição).
- Mensagens de erro abaixo do campo, curtas e objetivas.

## 8) Ícones e ilustrações

- Ícones simples, traço limpo e estilo consistente.
- Evitar mistura de estilos (outline e preenchido) no mesmo contexto.
- Ilustrações apenas quando agregarem compreensão, sem poluição visual.

## 9) Interações e estados (com htmx)

- Toda ação assíncrona deve indicar estado (`loading`, sucesso, erro).
- Usar transições rápidas e sutis (`120ms` a `180ms`) em hover/foco.
- Evitar animações longas ou distrações.
- Em atualizações parciais com `htmx`, preservar contexto do usuário na tela.

## 10) Acessibilidade

- Garantir contraste mínimo WCAG AA para texto e botões.
- Área clicável mínima confortável (ideal >= `40x40px`).
- Navegação por teclado funcional em todos os fluxos principais.
- Nunca comunicar status apenas por cor; adicionar texto/ícone de suporte.

## 11) Linguagem e localização (Brasil)

- Idioma padrão e obrigatório da interface: `pt-BR`.
- Textos, mensagens, labels e validações devem estar em português do Brasil.
- Formatos devem seguir padrão brasileiro:
  - Data: `dd/mm/aaaa`
  - Hora: `HH:mm`
  - Moeda: `R$ 1.234,56`
- Tom de voz: claro, humano e direto, adequado ao público brasileiro.

## 12) CSS tokens base (referência)

```css
:root {
  --rl-primary: #1d4ed8;
  --rl-secondary: #0ea5a4;
  --rl-accent: #f59e0b;

  --rl-bg: #f8fafc;
  --rl-surface: #ffffff;
  --rl-text: #0f172a;
  --rl-text-muted: #64748b;
  --rl-border: #e2e8f0;

  --rl-success: #16a34a;
  --rl-warning: #d97706;
  --rl-danger: #dc2626;
  --rl-info: #2563eb;

  --rl-radius-sm: 8px;
  --rl-radius-md: 12px;
  --rl-radius-lg: 16px;
}
```

## 13) Checklist rápida de revisão visual

- A tela está limpa e com boa hierarquia?
- Botões seguem o mesmo padrão?
- Cards mantêm borda, raio e espaçamento definidos?
- Contraste e foco por teclado estão corretos?
- Fluxos com `htmx` mostram claramente estado de carregamento e retorno?
- Toda a interface está em `pt-BR` e com formatos brasileiros?
