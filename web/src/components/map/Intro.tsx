// Project introduction shown as a large modal over the landing map (was the old homepage).
import { useEffect, useRef } from 'react';
import type { Lang } from './strings';

type View = 'overview' | 'change' | 'landcover' | 'confidence' | 'sar';

const C = {
	en: {
		kicker: 'NASA Space Apps Challenge 2026 · Challenge: Dancing with the SARs',
		title: 'NISAR L-band Change Detection and Land Cover Mapping',
		team: 'Team 2936-ThanhNoi (NS05005) · Ninh Hải Đăng (lead), Phạm Minh Quang, Lê Toàn Thắng',
		lead: "NISAR's L-band radar looks through two weeks of cloud over Hưng Yên, Vietnam. From three validated acquisitions (22 Oct – 3 Nov 2026) we detect where water was let in and map land cover from radar alone, and we show how far those results can be trusted.",
		stats: [
			['3', 'NISAR GCOV acquisitions (VALIDATED)'],
			['2,572 km²', 'Hưng Yên province'],
			['~32%', 'cloud-free in Sentinel-2 over the same 12 days'],
			['1.6 km²', 'new water in one block, cause unverified'],
			['≈93%', 'balanced accuracy on pure cells, not map accuracy'],
		],
		steps: [
			{ t: '1 · Clouds hide the delta', d: 'Sentinel-2 saw only about a third of the province cloud-free. NISAR L-band SAR sees through cloud. We use its three passes: 22 Oct and 3 Nov (same descending track, 20 m) and 27 Oct (ascending, 10 m).', view: 'sar', doc: '/data/nisar/' },
			{ t: '2 · Something filled with water', d: '99.89% of the province did not change significantly between 22 Oct and 3 Nov. The largest change is a ~1.6 km² block beside a river where HH and HV both fell by about 6 dB, the signature of a smooth water surface.', view: 'change', doc: '/results/change/' },
			{ t: '3 · Land cover from radar only', d: '1,347 hand-drawn polygons and 12 SAR features train a Random Forest that maps water, vegetation, bare soil and built-up land for the whole province, including the parts under cloud.', view: 'landcover', doc: '/results/landcover/' },
			{ t: '4 · How much to trust it', d: 'Ten models agree on 65.9% of the area; 8.3% lies outside the area of applicability; built-up is the least reliable class. Eight experiments document this.', view: 'confidence', doc: '/limitations/' },
		],
		showMap: 'Show on map', read: 'Read more',
		linksTitle: 'Documentation',
		links: [['Overview', '/overview/'], ['Data', '/data/nisar/'], ['Methods', '/methods/change-detection/'], ['Experiments E1–E8', '/experiments/'], ['Results', '/results/change/'], ['Limitations', '/limitations/'], ['Reproduce', '/reproduce/'], ['FAQ', '/faq/'], ['Team', '/team/']],
		chat: '💬 Ask the AI assistant', explore: 'Explore the map →', close: 'Close',
	},
	vi: {
		kicker: 'NASA Space Apps Challenge 2026 · Đề bài: Dancing with the SARs',
		title: 'NISAR L-band Change Detection and Land Cover Mapping',
		sub: 'Phát hiện biến động và phân loại lớp phủ bằng ảnh NISAR băng L',
		team: 'Đội 2936-ThanhNoi (NS05005) · Ninh Hải Đăng (trưởng nhóm), Phạm Minh Quang, Lê Toàn Thắng',
		lead: 'Radar băng L của NISAR nhìn xuyên lớp mây che Hưng Yên suốt hai tuần. Từ ba ảnh VALIDATED (22/10 đến 3/11/2026), chúng tôi tìm nơi được cho nước vào, lập bản đồ lớp phủ chỉ bằng radar, và nói rõ kết quả đáng tin đến đâu.',
		stats: [
			['3', 'ảnh NISAR GCOV (VALIDATED)'],
			['2.572 km²', 'tỉnh Hưng Yên'],
			['~32%', 'diện tích có ảnh Sentinel-2 không mây trong 12 ngày'],
			['1,6 km²', 'nước mới trong một khối, chưa rõ nguyên nhân'],
			['≈93%', 'độ chính xác cân bằng trên ô thuần, không phải độ chính xác bản đồ'],
		],
		steps: [
			{ t: '1 · Mây che kín đồng bằng', d: 'Sentinel-2 chỉ thấy khoảng một phần ba diện tích tỉnh không mây. SAR băng L của NISAR nhìn xuyên mây. Chúng tôi dùng ba lượt chụp: 22/10 và 3/11 (cùng track xuống, 20 m) và 27/10 (track lên, 10 m).', view: 'sar', doc: '/data/nisar/' },
			{ t: '2 · Một khu được cho nước vào', d: '99,89% diện tích tỉnh không đổi đáng kể giữa 22/10 và 3/11. Thay đổi lớn nhất là một khối khoảng 1,6 km² cạnh sông, nơi HH và HV đều giảm khoảng 6 dB, dấu hiệu của mặt nước phẳng.', view: 'change', doc: '/results/change/' },
			{ t: '3 · Lớp phủ chỉ từ radar', d: '1.347 polygon nhãn vẽ tay và 12 đặc trưng SAR huấn luyện Random Forest, lập bản đồ nước, thực vật, đất trống và đô thị/làng cho toàn tỉnh, kể cả vùng bị mây che.', view: 'landcover', doc: '/results/landcover/' },
			{ t: '4 · Tin được đến đâu', d: 'Mười mô hình cùng một lớp ở 65,9% diện tích; 8,3% diện tích nằm ngoài vùng áp dụng; đô thị là lớp kém tin cậy nhất. Tám thí nghiệm ghi lại điều này.', view: 'confidence', doc: '/limitations/' },
		],
		showMap: 'Xem trên bản đồ', read: 'Đọc thêm',
		linksTitle: 'Tài liệu',
		links: [['Tổng quan', '/overview/'], ['Dữ liệu', '/data/nisar/'], ['Phương pháp', '/methods/change-detection/'], ['Thí nghiệm E1–E8', '/experiments/'], ['Kết quả', '/results/change/'], ['Giới hạn', '/limitations/'], ['Tái tạo kết quả', '/reproduce/'], ['Hỏi đáp', '/faq/'], ['Đội thi', '/team/']],
		chat: '💬 Hỏi trợ lý AI', explore: 'Khám phá bản đồ →', close: 'Đóng',
	},
};

export default function Intro({ lang, onClose, onView, onChat }: { lang: Lang; onClose: () => void; onView: (v: View) => void; onChat: () => void }) {
	const c = C[lang] as (typeof C)['vi'];
	const p = lang === 'vi' ? '/vi' : '';
	const box = useRef<HTMLDivElement>(null);
	useEffect(() => {
		const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
		window.addEventListener('keydown', k);
		box.current?.focus();
		return () => window.removeEventListener('keydown', k);
	}, [onClose]);

	return (
		<div className="dwts-intro-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
			<div className="dwts-intro" role="dialog" aria-modal="true" aria-labelledby="dwts-intro-title" tabIndex={-1} ref={box}>
				<button className="dwts-close" onClick={onClose} aria-label={c.close}>✕</button>
				<p className="dwts-intro-kicker">{c.kicker}</p>
				<h1 id="dwts-intro-title">{c.title}</h1>
				{c.sub && <p className="dwts-intro-sub">{c.sub}</p>}
				<p className="dwts-intro-team">{c.team}</p>
				<p className="dwts-intro-lead">{c.lead}</p>
				<div className="dwts-intro-stats">
					{c.stats.map(([b, s]) => <div key={s}><b>{b}</b><span>{s}</span></div>)}
				</div>
				<div className="dwts-intro-steps">
					{c.steps.map((st) => (
						<div key={st.t} className="dwts-intro-step">
							<h3>{st.t}</h3>
							<p>{st.d}</p>
							<div>
								<button onClick={() => onView(st.view as View)}>🗺 {c.showMap}</button>
								<a href={p + st.doc}>{c.read} →</a>
							</div>
						</div>
					))}
				</div>
				<div className="dwts-intro-foot">
					<div className="dwts-intro-links">
						<b>{c.linksTitle}:</b> {c.links.map(([n, u]) => <a key={u} href={p + u}>{n}</a>)}
					</div>
					<div className="dwts-intro-actions">
						<button className="secondary" onClick={onChat}>{c.chat}</button>
						<button className="primary" onClick={onClose}>{c.explore}</button>
					</div>
				</div>
			</div>
		</div>
	);
}
