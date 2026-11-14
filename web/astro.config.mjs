// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import react from '@astrojs/react';
import node from '@astrojs/node';

const group = (en, vi, directory) => ({
	label: en,
	translations: { vi },
	items: [{ autogenerate: { directory } }],
});

export default defineConfig({
	site: 'https://dwts.ninhhaidang.com',
	adapter: node({ mode: 'standalone' }),
	integrations: [
		react(),
		starlight({
			title: { en: 'NISAR L-band Change Detection and Land Cover Mapping', vi: 'Phát hiện biến động và phân loại lớp phủ bằng ảnh NISAR băng L' },
			description:
				'NISAR L-band Change Detection and Land Cover Mapping: NISAR L-band SAR over Hưng Yên, Vietnam. Team 2936-ThanhNoi (NS05005), NASA Space Apps Challenge 2026, challenge Dancing with the SARs.',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/ninhhaidang/ns05005-dancing-with-the-sars' }],
			defaultLocale: 'root',
			locales: {
				root: { label: 'English', lang: 'en' },
				vi: { label: 'Tiếng Việt', lang: 'vi' },
			},
			logo: { src: './src/assets/logo.svg', replacesTitle: false },
			customCss: ['./src/styles/custom.css'],
			components: {
				Footer: './src/components/Footer.astro',
			},
			lastUpdated: false,
			sidebar: [
				{
					label: 'Explore',
					translations: { vi: 'Khám phá' },
					items: [
						{ label: 'Interactive map', translations: { vi: 'Bản đồ tương tác' }, link: '/map/' },
						{ label: 'Ask the assistant', translations: { vi: 'Hỏi trợ lý AI' }, link: '/chat/' },
					],
				},
				{
					label: 'Project',
					translations: { vi: 'Dự án' },
					items: [
						{ slug: 'overview' },
						{ slug: 'limitations' },
						{ slug: 'reproduce' },
						{ slug: 'faq' },
						{ slug: 'glossary' },
						{ slug: 'team' },
					],
				},
				group('Data', 'Dữ liệu', 'data'),
				group('Methods', 'Phương pháp', 'methods'),
				group('Experiments', 'Thí nghiệm', 'experiments'),
				group('Results', 'Kết quả', 'results'),
			],
		}),
	],
	vite: { optimizeDeps: { exclude: ['maplibre-gl'] } },
});
